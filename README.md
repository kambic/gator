# MediaCMS
npm config set strict-ssl false
yarn config set strict-ssl false
https://github.com/puikinsh/Bootstrap-Admin-Template
[![pipeline status](https://gitlab.telekom.si/vidra/mediacms/badges/main/pipeline.svg)](https://gitlab.telekom.si/vidra/mediacms/-/commits/master)
[![coverage report](https://gitlab.telekom.si/vidra/mediacms/badges/master/coverage.svg)](https://gitlab.telekom.si/vidra/mediacms/-/commits/master)
[![Latest Release](https://gitlab.telekom.si/vidra/mediacms/-/badges/release.svg)](https://gitlab.telekom.si/vidra/mediacms/-/releases)

![Build Status](https://img.shields.io/badge/python-3-blue)
![PyPI](https://img.shields.io/badge/pypi_version-0.0.0-green)

MediaCMS is a modern, fully featured open source video and media CMS. It is developed to meet the needs of modern web platforms for viewing and sharing media. It can be used to build a small to medium video and media portal within minutes.

It is built mostly using the modern stack Django + React and includes a REST API.


## Screenshots

<p align="center">
    <img src="https://gitlab.telekom.si/vidra/mediacms/-/raw/master/docs/images/index.jpg" width="340">
    <img src="https://gitlab.telekom.si/vidra/mediacms/-/raw/master/docs/images/video.jpg" width="340">
    <img src="https://gitlab.telekom.si/vidra/mediacms/-/raw/master/docs/images/embed.jpg" width="340">
</p>

## Features
- **Complete control over your data**: host it yourself!
- **Modern technologies**: Django/Python/Celery, React.
- **Support for multiple publishing workflows**: public, private, unlisted and custom
- **Role-Based Access Control (RBAC)**: create RBAC categories and connect users to groups with view/edit access on their media
- **Automatic transcription**: through integration with Whisper running locally
- **Multiple media types support**: video, audio,  image, pdf
- **Multiple media classification options**: categories, tags and custom
- **Multiple media sharing options**: social media share, videos embed code generation
- **Video Trimmer**: trim video, replace, save as new or create segments
- **SAML support**: with ability to add mappings to system roles and groups
- **Easy media searching**: enriched with live search functionality
- **Playlists for audio and video content**: create playlists, add and reorder content
- **Responsive design**: including light and dark themes
- **Advanced users management**: allow self registration, invite only, closed.
- **Configurable actions**: allow download, add comments, add likes, dislikes, report media
- **Configuration options**: change logos, fonts, styling, add more pages
- **Enhanced video player**: customized video.js player with multiple resolution and playback speed options
- **Multiple transcoding profiles**: sane defaults for multiple dimensions (144p, 240p, 360p, 480p, 720p, 1080p) and multiple profiles (h264, h265, vp9)
- **Adaptive video streaming**: possible through HLS protocol
- **Subtitles/CC**: support for multilingual subtitle files
- **Scalable transcoding**: transcoding through priorities. Experimental support for remote workers
- **Chunked file uploads**: for pausable/resumable upload of content
- **REST API**: Documented through Swagger
- **Translation**: Most of the CMS is translated to a number of languages


## Documentation

* [Users documentation](docs/user_docs.md) page
* [Administrators documentation](docs/admins_docs.md) page
* [Developers documentation](docs/developers_docs.md) page
* [Configuration](docs/admins_docs.md#5-configuration) page
* [Transcoding](docs/transcoding.md) page
* [Developer Experience](docs/dev_exp.md) page
* [Media Permissions](docs/media_permissions.md) page


## Technology

This software uses the following list of awesome technologies: Python, Django, Django Rest Framework, Celery, PostgreSQL, Redis, Nginx, uWSGI, React, Fine Uploader, video.js, FFMPEG, Bento4
