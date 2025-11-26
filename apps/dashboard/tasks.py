# your_app/ping.py
import os
import zipfile

from celery import shared_task


@shared_task
def start_vod_ingest_task(zip_file_path):
    """
    Celery task to handle VOD ingestion from a ZIP file.
    """
    if not os.path.exists(zip_file_path):
        # Log and return if file not found
        return f"Error: File not found at {zip_file_path}"

    ingest_status = {
        'file': os.path.basename(zip_file_path),
        'status': 'STARTED',
        'details': [],
    }

    try:
        # 1. Validate and extract the ZIP file
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            # You might want to extract to a temporary, working directory
            # For this example, we'll just iterate over contents
            for member in zip_ref.namelist():
                # 2. Ingest Logic (Example Steps)

                # Check for main manifest/video file
                if member.endswith(('.mp4', '.m3u8', '.mpd', '.json')):
                    # Example: Read or extract file content and create DB records
                    # This is where your actual VOD ingestion logic goes, e.g.,
                    # - Save a record to the VOD model
                    # - Trigger FFmpeg processing for streams
                    # - Move the file to a permanent storage location

                    ingest_status['details'].append(f"Processing: {member}")

            # 3. Cleanup: Move or delete the source ZIP file
            # os.remove(zip_file_path) # <-- UNCOMMENT WHEN READY FOR DELETION
            ingest_status['status'] = 'SUCCESS'

    except zipfile.BadZipFile:
        ingest_status['status'] = 'FAILED'
        ingest_status['details'].append("Error: Not a valid ZIP file.")

    except Exception as e:
        ingest_status['status'] = 'FAILED'
        ingest_status['details'].append(f"Ingest failed due to error: {str(e)}")

    # Log the final status (you should use a proper logging system)
    print(f"Ingest Result for {zip_file_path}: {ingest_status['status']}")

    return ingest_status



def schedule_validation_jobs():
    for media_file in MediaFile.objects.filter(file_type="hls", status="ready"):
        validate_media_file.delay(media_file.id)

    from celery import shared_task
    from django.contrib.auth.models import User
    # from media.models import Media  # Adjust based on MediaCMS's model path
    # from edgeware.models import Edgeware  # Adjust based on your app name
    import requests
    from django.db import transaction
    from celery.utils.log import get_task_logger

    logger = get_task_logger(__name__)

    @shared_task(bind=True, max_retries=3)
    def migrate_edgeware_to_mediacms(self, batch_size=1000, start_id=0):
        """
        Migrate Edgeware entries to MediaCMS Media model in batches.
        Fetches HLS, DASH, MSS URLs from Edgeware API and maps to Media model.
        """
        try:
            # Get admin user for assigning media (adjust as needed)
            admin_user = User.objects.filter(is_superuser=True).first()
            if not admin_user:
                raise Exception("No admin user found for media assignment")

            # Query Edgeware entries in batch
            edgeware_entries = Edgeware.objects.filter(
                status=Edgeware.Status.EW_SUCCESS,
                id__gt=start_id
            ).order_by('id')[:batch_size]

            if not edgeware_entries.exists():
                logger.info("No more Edgeware entries to process")
                return

            media_objects = []
            for entry in edgeware_entries:
                try:
                    # Fetch streaming URLs from Edgeware API
                    api_url = f"https://edgeware-api.example.com/api/asset/{entry.ew_id}/streams"
                    response = requests.get(api_url, timeout=10)
                    response.raise_for_status()
                    stream_data = response.json()

                    # Create or update Media object
                    media, created = Media.objects.get_or_create(
                        ew_id=entry.ew_id,
                        defaults={
                            'title': entry.title or f"Edgeware_{entry.ew_id}",
                            'user': admin_user,
                            'status': 'published',  # Adjust based on MediaCMS status
                            'hls_url': stream_data.get('hls'),
                            'dash_url': stream_data.get('dash'),
                            'mss_url': stream_data.get('mss'),
                            'file_path': entry.ftp_dir or '',  # Map to original file if available
                        }
                    )

                    if not created:
                        # Update existing media
                        media.hls_url = stream_data.get('hls')
                        media.dash_url = stream_data.get('dash')
                        media.mss_url = stream_data.get('mss')
                        media.title = entry.title or media.title
                        media.file_path = entry.ftp_dir or media.file_path

                    media_objects.append(media)

                    # Update Edgeware status
                    entry.status = Edgeware.Status.ETL
                    entry.msg = {'migration': 'success', 'media_id': media.id}
                    entry.save()

                except requests.RequestException as e:
                    # Handle API errors
                    entry.status = Edgeware.Status.EW_ERROR
                    entry.msg = {'error': f"API call failed: {str(e)}"}
                    entry.save()
                    logger.error(f"Failed to fetch streams for ew_id {entry.ew_id}: {e}")
                    continue
                except Exception as e:
                    # Handle other errors
                    entry.status = Edgeware.Status.EW_ERROR
                    entry.msg = {'error': str(e)}
                    entry.save()
                    logger.error(f"Error processing ew_id {entry.ew_id}: {e}")
                    continue

            # Bulk update Media objects
            if media_objects:
                with transaction.atomic():
                    Media.objects.bulk_update(
                        media_objects,
                        ['title', 'hls_url', 'dash_url', 'mss_url', 'file_path']
                    )
                logger.info(f"Processed {len(media_objects)} Edgeware entries")

            # Schedule next batch
            last_id = edgeware_entries.last().id if edgeware_entries else start_id
            migrate_edgeware_to_mediacms.delay(batch_size=batch_size, start_id=last_id)

        except Exception as e:
            logger.error(f"Task failed: {e}")
            self.retry(countdown=60, exc=e)
