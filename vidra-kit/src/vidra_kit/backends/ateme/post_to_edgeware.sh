#!/bin/bash

# lipniks@btl-bmov-01:~/ateme$ cat post-to-edgeware.sh

# Export environment variables
export EW_KEY="wgXfC6EHEAjQt8wvzErgRE"
export EW_API="http://ew-api.tv.telekom.si:8090/api/2/content"
export EW_SECRET="kdmgj7390s"
export MTCMT_STAG="mtcms-stag.mmv.si"
export MTCMS_STAG_API_KEY="MTCMS_API_TOK eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODk234324wIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.PxnqfjHUk0MTwlL9t7EYWPT3AsfgzwCa_5v038hOoMk"
export MTCMT_PROD="mtcms.mmv.si"
export MTCMS_PROD_API_KEY="MTCMS_API_TOK eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0c2RhNTY3ODkwIiwibmFtZSI6IkpvaGRzYXNhZG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.KRj7Nv_a2Q4O4029fYXmn_oLQYwBRFaa3CyJ28ZORGk"

# Function to generate a random UUID and store it
generate_content_id() {
	CONTENT_ID=$(uuidgen)
	echo "Generated content_id: $CONTENT_ID"
}

# Function to copy files to FTP
copy_files_to_ftp() {
	FTP_SERVER="isilj.ts.telekom.si"
	FTP_USER="ftpott"
	FTP_PASS="ft17pott"
	REMOTE_DIR="vod/staging-test-1"
	LOCAL_DIR="/home/lipniks/ateme/upload"

	# Check if the local directory exists
	if [ ! -d "$LOCAL_DIR" ]; then
		echo "Error: Local directory $LOCAL_DIR does not exist."
		exit 1
	fi

	echo "Uploading files from $LOCAL_DIR to FTP $FTP_SERVER:$REMOTE_DIR..."

	# Start FTP session and upload all files
	ftp -inv $FTP_SERVER <<EOF
user $FTP_USER $FTP_PASS
cd $REMOTE_DIR
pwd
lcd $LOCAL_DIR
bin
mput *.mp4
ascii
mput *.mpd
bye
EOF

	echo "All files from $LOCAL_DIR uploaded successfully to $FTP_SERVER:$REMOTE_DIR"
}

upload_thumbnails_to_cdn() {
	#xvodvtt:YD6TbjhTcTw@fpw-cdn03.ts.telekom.si:21
	# External URL: https://cdn.siol.tv/sioltv/xvodvtt/staging-test-1/thumbs.vtt
	# External URL: https://cdn.siol.tv/sioltv/xvodvtt/staging-test-1/thumbs_0.jpg
	# Varnish External: https://ngimg.siol.tv/sioltv/xvodvtt/staging-test-1/thumbs.vtt
	FTP_SERVER2="fpw-cdn03.ts.telekom.si"
	FTP_USER2="xvodvtt"
	FTP_PASS2="YD6TbjhTcTw"
	REMOTE_DIR2="/staging-test-1"
	LOCAL_DIR2="/home/lipniks/ateme/upload"

	# Check if the local directory exists
	if [ ! -d "$LOCAL_DIR2" ]; then
		echo "Error: Local directory $LOCAL_DIR2 does not exist."
		exit 1
	fi

	echo "Uploading files from $LOCAL_DIR2 to FTP $FTP_SERVER2:$REMOTE_DIR2..."

	# Function to upload thumbnails to CDN
	echo "Uploading thumbnails to CDN..."
	# Add your CDN upload logic here
	ftp -inv $FTP_SERVER2 <<EOF
user $FTP_USER2 $FTP_PASS2
cd $REMOTE_DIR2
lcd $LOCAL_DIR2
bin
mput *.jpg
ascii
mput *.vtt
bye
EOF

	echo "All files from $LOCAL_DIR2 uploaded successfully to $FTP_SERVER2:$REMOTE_DIR2"

}

# Function to call Edgeware API and extract the "dash" URL
edgeware_api() {
	echo "Calling Edgeware API with content_id: $CONTENT_ID..."

	# Call API and store response
	RESPONSE=$(curl -s -X POST \
		-H "x-account-api-key: ${EW_KEY}" \
		-H "Content-Type: application/json" \
		-d '{
        "service": "HTTP",
        "source": "upload",
        "content_id": "'"$CONTENT_ID"'",
        "title": "staging-test-1",
        "upload": {
            "location": "file:///mnt/storage-lj/vod/staging-test-1/manifest.mpd"
        }
    }' ${EW_API})

	echo "Edgeware API Response: $RESPONSE"

	# Extract "dash" value using jq
	DASH_URL=$(echo "$RESPONSE" | jq -r '.delivery_uris.dash')
	HLS_URL=$(echo "$RESPONSE" | jq -r '.delivery_uris.hls')

	# Debugging: Print parsed JSON
	echo "Parsed JSON output:"
	echo "$RESPONSE" | jq .

	# Check if jq successfully extracted the value
	if [ -z "$DASH_URL" ] || [ "$DASH_URL" == "null" ]; then
		echo "Error: Failed to extract 'dash' URL from API response."
		exit 1
	fi

	#echo "Extracted DASH URL: $DASH_URL"
	#echo "Extracted HLS URL: $HLS_URL"
}

post_subtitles_to_mtcms_stag() {

	curl --location 'https://mtcms.mmv.si/api/offer' \
		--header 'Authorization: MTCMS-API-TOK .......' \
		--header 'Content-Type: application/json' \
		--data '{"mappedOfferId":"VOD_CATALOGUE_fa7d4c23f6f82969e9cfdf96", "vtt":"http://haha.ha"}'

}
create_streaming_links() {
	secret_key=$EW_SECRET
	# Fake SSL certificate is not working from TS network
	#client_ip="$(curl ifconfig.io)"

	#This is main FW IP that is used for STBs when they are in the network
	client_ip="213.250.0.222"

	#This is my external IP from the workstation
	echo "---------------------------------------------------------------------------------"
	echo "We are using this IP for link and token generation..."
	#client_ip="213.229.248.10"
	echo $client_ip
	echo "---------------------------------------------------------------------------------"

	#This is my home static IP
	#client_ip="193.77.159.160"
	expiration="$(date -d "+1 day" +%s)"

	modified_dash="${DASH_URL#/}"
	modified_hls="${HLS_URL#/}"

	content_dash=$modified_dash
	content_hls=$modified_hls
	token1="$secret_key$content_dash$client_ip$expiration"
	token2="$secret_key$content_hls$client_ip$expiration"
	#echo $token
	token1="$(echo -n $token | md5sum | awk '{print $1}')"
	token2="$(echo -n $token | md5sum | awk '{print $1}')"
	echo "Generating streaming links..."
	echo "---------------------------------------------------------------------------------"
	echo "PROD URL DASH: https://rr.sdn.si/$content_dash?token=$token1&expires=$expiration"
	echo "PROD URL HLS: https://rr.sdn.si/$content_hls?token=$token2&expires=$expiration"
	echo "---------------------------------------------------------------------------------"
	echo "LAB URL DASH: http://ew-backend-01.tv.telekom.si/$content_dash"
	echo "LAB URL HLS: http://ew-backend-01.tv.telekom.si/$content_hls"
	echo "---------------------------------------------------------------------------------"

	#base="$(echo -n "https://rr.sdn.si/$content_hls?token=$token&expires=$expiration" | base64 -w0)"

	#echo "Base64 URL: $base"
	#adbcom='adb shell am broadcast -a si.titan.stb.action.NAVIGATION --es si.titan.stb.extra.NavigationPath "app://player/base64/'$base'"'

	#echo $adbcom
	#echo "ADB command: $adbcom"
	#$adbcom
}
# Run the functions in sequence
generate_content_id
copy_files_to_ftp
sleep 2
edgeware_api
sleep 2
create_streaming_links
sleep 2
upload_thumbnails_to_cdn
sleep 2
