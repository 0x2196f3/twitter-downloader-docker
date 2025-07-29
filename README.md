# Twitter-Downloader-Docker

download users' all images and videos by twitter-id every 24 hours in a docker container (account cookies required, no twitter api required)   
### based on [twitter_download](https://github.com/caolvchong-top/twitter_download)

## Supported Architectures  
- linux/amd64  
- linux/arm64    
   
## Environment Variables
| Environment Variable | Usage |
| --- | --- |
| `INTERVAL` | Try downloading tweets every `$INTERVAL` seconds, default=60 * 60 * 24=24 hours, min=60=1 miniute |
| `RETRY_TIMES` | Retry times when [twitter_download](https://github.com/caolvchong-top/twitter_download) exit with code other than 0, default=1, max=10 |
| `DELETE_CSV` | Delete auto generated *.csv files, default=false. If downloaded images/videos still exist in /downloads, it seems that twitter_download will not download existing files again even if without *.csv files.  |

## Volume Mapping
| Container Directory | Description                                                               |
| --- |---------------------------------------------------------------------------|
| `/download` | tweets will be downloaded here, organized by username                     |
| `/config/settings.json` | [twitter_download/settings.json](https://github.com/caolvchong-top/twitter_download/blob/main/settings.json), can't be empty. The program copy /config/settings.json to working dir on every schedule, no restart is needed after editing settings.json. |


## Usage
```bash
docker run -d --name=twitter-downloader-docker -v /path/to/config:/config -v /path/to/download:/download -e INTERVAL=43200 -e RETRY_TIMES=3 -e DELETE_CSV=true docker.io/0x2196f3/twitter-downloader-docker
```
