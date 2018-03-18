# Webcam post processing

## Basic usage

very basic connection to image source

```shell 
 $ python manage.py start_daemon -d [config folder]
```

## Configuration

there is folder with configuration files, each file represent one postprocess source and process definition. 

configuration structure is simple Yaml file

```
- - -
#
# very basic config structure
#
source:
  [source type]:
    [parameters]

data_resource:
  [resource type]:
    [name]:
        [parameters]

machinery:
  decorations:
    [decoration type]
      [parameters]
    [decoration type]
      [parameters]
    [decoration type]
      [parameters]
    ...
  storage:
    [storage type]
      [parameters] 
    [storage type]
      [parameters] 
    ...
              
machinery:
  decorations:
    [decoration type]
      [parameters]
    ...
  storages:
    [storage type]
      [parameters] 
    [storage type]
      [parameters] 
    ...

...


```

in config could be many decorations, for every decoration is the same source original file. Recommended steps are
 *  crop
 *  resize 
 *  add alpha images
 *  add images
 *  add texts 
 *  send to target

### Sources

for begin we start with Rabbit MQ. For next will be HTTP or file system sources. The most important will be notification 
about new image. The Rabbit MQ this solve by design, so it is not necessary to thing about it.  

#### Folder watch

look up in folder for changes  IN_CLOSE_WRITE, if there is file what match the `filter_reg_ex`  than is processed. 
Be careful about storage folder what have to be different or target file should not mach `filter_reg_ex` pattern, this 
could generate an error or infinite loop.

```yaml

source:
  folder_watch:
    source: "/path/to/image/source"
    filter_reg_ex: "^my_file.*$"
    
```

#### Rabbit MQ

read data from RMQ exchange (create queue and bind exchange with routing key)

```yaml

source:
  rabbitmq:
    uri: "rmqs://user:pass@host:port/vhost"
    cert: "path to certificate"
    key: "path to private key"
    cacert: "path to CA certificate"
    queue: "name of queue" 
    exchange: "exchange name"
    bind: "bind ID"
    message_ttl: "mesage TTL in miliseconds"
    heartbeat: "keepalive time in seconds, default is 30"
    socket_timeout: "connection  timeout, default is 60"
  
   
```

### Data resources

usually this is used for image text information, but it could be anything like analog clock image or chart stored in image.
Very basic is graphite resource
```
data_resource:
  [resource type]:
    [name]:
        [parameters]
```
#### Resource type: Graphite

##### Parameters

 * **URL** graphite render source
 * **start_time** time in graphite usual format
 * **end_time** declare end of period
 * **dimensions** list of dimensions
 ** **dimension_name**: dimension source
 * **timeout** optional, but important for graphite is down or slow (default is 10s) 


### Decoration types

```
decorations:
  [decoration type]
    [parameters]
  ...
    
```

#### Decoration: Crop

Crop image, all coordinates are from top left corner

 * **x** top horizontal position  
 * **x** top vertical position  
 * **width** crop width 
 * **height** crop height
  
#### Decoration: Resize

Resize image 

 * **width** new image width 
 * **height** new image height
 
#### Decoration: Alpha background 

usually background for text, what should be somehow transparent

 * **color** RGB color
 * **alpha** alpha index from 0 to 1
 * **topX** top horizontal position  
 * **topY** top vertical position  
 * **bottomX** bottom horizontal position 
 * **bottomY** bottom vertical position
 

#### Decoration: Imagger

place image like logos into picture

 * **source** path to image
 * **topX** top horizontal position  
 * **topY** top vertical position  
 * **width** placed image width
 * **height** placed image height


#### Decoration: Alpha_image

place transparent rectangle in image. 

 * **red** red part
 * **green** green RGB part
 * **blue** blue RGB part
 * **alpha** transparency index
 * **topX** top horizontal position  
 * **topY** top vertical position  
 * **width** placed image width
 * **height** placed image height


#### Decoration: Texts
 * **lines**: 
 ** - "text line with django template placeholders"
 * **topX** top horizontal position  
 * **topY** top vertical position  
 * **font** font name reference
 * **size** font size
 * **line_height** line spacing index (default is 1)
 
#### Store type

```
storages:
  [store type]
    [parameters]
  ...
```

after decoration should be image somewhere stored and system should be informed about this image

##### Storage type File

store file on local file system

 * **folder_name** directory template
 * **file_name** file name template

```yaml

machinery:
  storages:
    file:
      file_name: "file-{hour}-{minute}.jpg"
      folder_name: "/storage/folder"
```

##### Storage type FTP

store file on remote FTP server

 * **uri** FTP uri  
 * **base_dir** directory template
 * **file_template** file name template
 
 
##### Storage type RabbitMQArchive

store information about image in Rabbit MQ

 * **uri** rmqs://user:pass@host:port/vhost
 * **cert** path to certificate
 * **key** path to private key
 * **cacert** path to CA certificate
 * **queue** name of queue 
 * **exchange** exchange name
 * **bind** bind ID
 * **message_ttl** mesage TTL in miliseconds


##### Storage type DBArchive

this is direct DB storage
 
 * **db_name** database name 
 

