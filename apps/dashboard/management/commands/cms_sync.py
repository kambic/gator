import loguru
from asgiref.sync import sync_to_async

logger = loguru.logger

from apps.dashboard.models import Edgeware, Provider

import asyncio
import aiohttp

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Fetch data from API and update Django model asynchronously'

    async def fetch_data(self, url, session):
        """Fetch data from a given URL using aiohttp."""
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Failed to fetch data from {url}: Status {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error fetching data from {url}: {e}")
            return None

    async def update_item(self, item, session):
        """Fetch and update a single Item using its ID."""
        api_url = f'https://mtcms-stag.telekom.si/api/output/offer?mappedOfferId={item.offer_id}'
        item_data = await self.fetch_data(api_url, session)
        if not item_data:
            logger.error(f"No data received for item {item.id}")
            return

        if not item_data or not isinstance(item_data, dict) or 'offers' not in item_data:
            logger.error(f"No valid data received for item {item.id} (offer_id: {item.offer_id})")
            return

        if not item_data['offers']:
            logger.error(f"No offers found in data for item {item.id} (offer_id: {item.offer_id})")
            return

        try:
            # Update the item with fetched data
            offer = item_data['offers'][0]
            provider = offer['provider']['name']
            # Fetch provider asynchronously
            try:
                provider = await sync_to_async(Provider.objects.get)(
                    user__name=provider
                )
            except Provider.DoesNotExist:
                logger.error(
                    f"Provider with username '{provider}' not found for item {item.id} (offer_id: {item.offer_id})"
                )
                return

            item.provider = provider
            await sync_to_async(item.save)()

            logger.info(f"Successfully updated item with id {item.id}")
        except Exception as e:
            logger.error(f"Error updating item {item.id}: {e}")

    async def main(self):
        """Main async function to fetch and update each item separately."""
        # Get all existing items from the database
        items = await sync_to_async(lambda: list(Edgeware.expired_objects.filter(provider_id=None)[:10050]))()

        if not items:
            logger.info("No items found in the database to update.")
            return

        headers = {
            'Authorization': 'MTCMS-API-TOK eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0c2RhNTY3ODkwIiwibmFtZSI6IkpvaGRzYXNhZG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.KRj7Nv_a2Q4O4029fYXmn_oLQYwBRFaa3CyJ28ZORGk'
        }
        stag_headers = {
            'Authorization': 'MTCMS-API-TOK eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODk234324wIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.PxnqfjHUk0MTwlL9t7EYWPT3AsfgzwCa_5v038hOoMk'}

        async with aiohttp.ClientSession(headers=stag_headers) as session:
            # Create tasks for each item update
            tasks = [self.update_item(item, session) for item in items]
            await asyncio.gather(*tasks, return_exceptions=True)

    def handle(self, *args, **options):
        """Django command entry point."""
        try:
            # Run the async main function
            asyncio.run(self.main())
            self.stdout.write(self.style.SUCCESS('Successfully updated items'))
        except Exception as e:
            logger.error(f"Error in command: {e}")
            self.stdout.write(self.style.ERROR('Failed to update items'))
