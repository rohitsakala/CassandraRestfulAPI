# CassandraRestfulAPI
=====================

## Description

**CassandraRestfulAPI** project exposes the cassandra data tables with the help of Restful API's. The project follows the standard Restful API rules. This project is developed as Major project of the Cloud Computing course by Team 15. The project is developed using Python Driver provided by Datastax using Flask framework.

## Installation

### Flask

<code>$ sudo pip install Flask</code>

### Cassandra

Follow these steps to install python cassandra driver [Python Driver Cassandra](https://datastax.github.io/python-driver/installation.html)

## API's

## Keyspaces

- List all the Keyspaces

<code> [GET] http://127.0.0.1:5000/keyspaces/ </code>

- Get Info about a keyspace 

<code> [GET] http://127.0.0.1:5000/keyspaces/<keyspaceid> </code>

- Creates a new keyspace

<code> [POST] http://127.0.0.1:5000/keyspaces/ </code>

##### Body

-- { 'name' : <name> , 'replicationFactor' : <number> }

- Updates the keyspace

<code> [PUT] http://127.0.0.1:5000/keyspaces/<keyspaceid> </code>

##### Body

-- { 'replicationFactor' : <number> }

- Deletes the keyspace

<code> [DELETE] http://127.0.0.1:5000/keyspaces/<keyspaceid> </code>


$ sudo apt-get install software-properties-common
$ sudo add-apt-repository ppa:ubuntugis/ubuntugis-unstable
$ sudo apt-get update
$ sudo apt-get install gdal-bin libgdal-dev
</pre>

	To install the python GDAL bindings into your virtualenv you need to tell pip where to find the libgdal header files, so in your shell run:

	<pre>
	$ export CPLUS_INCLUDE_PATH=/usr/include/gdal
	$ export C_INCLUDE_PATH=/usr/include/gdal
	</pre>

### Install third-party dependencies
	The HOT Export pipeline depends on a number of third-party tools.

	<code>$ sudo apt-get install osmctools</code>

	<code>$ sudo apt-get install spatialite-bin libspatialite5 libspatialite-dev</code>

	<code>$ sudo apt-get install default-jre zip unzip</code>

#### Garmin

	Download the latest version of the __mkgmap__ utility for making garmin IMG files from [http://www.mkgmap.org.uk/download/mkgmap.html](http://www.mkgmap.org.uk/download/mkgmap.html)

	Download the latest version of the __splitter__ utility for splitting larger osm files into tiles. [http://www.mkgmap.org.uk/download/splitter.html](http://www.mkgmap.org.uk/download/splitter.html)

	Create a directory and unpack the <code>mkgmap</code> and <code>splitter</code> archives into it.

#### OSMAnd OBF

	For details on the OSMAnd Map Creator utility see [http://wiki.openstreetmap.org/wiki/OsmAndMapCreator](http://wiki.openstreetmap.org/wiki/OsmAndMapCreator)

	Download the OSMAnd MapCreator from [http://download.osmand.net/latest-night-build/OsmAndMapCreator-main.zip](http://download.osmand.net/latest-night-build/OsmAndMapCreator-main.zip).
	Unpack this into a directory somewhere.

### Install RabbitMQ

	HOT Exports depends on the **rabbitmq-server**. For more detailed installation instructions see [http://www.rabbitmq.com/install-debian.html](http://www.rabbitmq.com/install-debian.html).
	The default configuration should be fine for development purposes.

	<code>$ sudo apt-get install rabbitmq-server</code>

### Checkout the HOT Export Tool source

	In the hotosm project directory run:

	<code>$ git clone git@github.com:hotosm/osm-export-tool2.git</code>

### Install the project's python dependencies

	From the project directory, install the dependencies into your virtualenv:

	<code>$ pip install -r requirements-dev.txt</code>

	or

	<code>$ pip install -r requirements.txt</code>


### Project Settings

	Create a copy of <code>core/settings/dev_dodobas.py</code> and update to reflect your development environment.

	Look at <code>core/settings/project.py</code> and make sure you update or override the following configuration variables in your development settings:

	**EXPORT_STAGING_ROOT** = 'path to a directory for staging export jobs'

	**EXPORT_DOWNLOAD_ROOT** = 'path to a directory for storing export downloads'

	**EXPORT_MEDIA_ROOT** = '/downloads/' (map this url in your webserver to EXPORT_DOWNLOAD_ROOT to serve the exported files)

	**OSMAND_MAP_CREATOR_DIR** = 'path to directory where OsmAndMapCreator is installed'

	**GARMIN_CONFIG** = 'absolute path to utils/conf/garmin_config.xml'

	**OVERPASS_API_URL** = 'url of your local overpass api endpoint (see Overpass API below)'

	Update the <code>utils/conf/garmin_config.xml</code> file. Update the <code>garmin</code> and <code>splitter</code> elements to point to the
	absolute location of the <code>mkgmap.jar</code> and <code>splitter.jar</code> utilites.

	Once you've got all the dependencies installed, run <code>./manage.py migrate</code> to set up the database tables etc..
	Then run <code>./manage.py runserver</code> to run the server.
	You should then be able to browse to [http://localhost:8000/](http://localhost:8000/)

## Overpass API

	The HOT Exports service uses a local instance of [Overpass v07.52](http://overpass-api.de/) for data extraction.
	Detailed instructions for installing Overpass are available [here](http://wiki.openstreetmap.org/w/index.php?title=Overpass_API/Installation&redirect=no).

	Download a (latest) planet pbf file from (for example) [http://ftp.heanet.ie/mirrors/openstreetmap.org/pbf/](http://ftp.heanet.ie/mirrors/openstreetmap.org/pbf/).

	If you're doing development you don't need the whole planet so download a continent or country level extract from [http://download.geofabrik.de/](http://download.geofabrik.de/),
	and update the `osmconvert` command below to reflect the filename you've downloaded.

	To prime the database we've used `osmconvert` as follows:

	<code>osmconvert --out-osm planet-latest.osm.pbf | ./update_database --meta --db-dir=$DBDIR --flush-size=1</code>

	If the dispatcher fails to start, check for, and remove <code>osm3s_v0.7.52_osm_base</code> from <code>/dev/shm</code>.

	We apply minutely updates as per Overpass installation instructions, however this is not strictly necessary for development purposes.

## Celery Workers

	HOT Exports depends on the [Celery](http://celery.readthedocs.org/en/latest/index.html) distributed task queue. As export jobs are created
	they are pushed to a Celery Worker for processing. At least two celery workers need to be started as follows:

	From a 'hotosm' virtualenv directory (use screen), run:

	<code>export DJANGO_SETTINGS_MODULE=core.settings.your_settings_module</code>

	<code>$ celery -A core worker --loglevel debug --logfile=celery.log</code>.

	This will start a celery worker which will process export tasks. An additional celery worker needs to be started to handle purging of expired unpublished
	export jobs. From another hotosm virtualenv terminal session in the project top-level directory, run:

	<code>export DJANGO_SETTINGS_MODULE=core.settings.your_settings_module</code>

	<code>$ celery -A core beat --loglevel debug --logfile=celery-beat.log</code>

	See the <code>CELERYBEAT_SCHEDULE</code> setting in <code>core/settings/celery.py</code>.

	For more detailed information on Celery Workers see [here](http://celery.readthedocs.org/en/latest/userguide/workers.html)

	For help with daemonizing Celery workers see [here](http://celery.readthedocs.org/en/latest/tutorials/daemonizing.html)

## Using Transifex service

	To work with Transifex you need to create `~/.transifexrc`, and modify it's access privileges

	`chmod 600 ~/.transifexrc`

	Example `.transifexrc` file:

	    [https://www.transifex.com]
	        hostname = https://www.transifex.com
		    password = my_super_password
		        token =
			    username = my_transifex_username

### Managing source files

			    To update source language (English) for Django templates run:

			    `python manage.py makemessages -l en`

			    To update source language for javascript files run:

			    `python manage.py makemessages -d djangojs -l en`


			    then, push the new source files to the Transifex service, it will overwrite the current source files

			    `tx push -s`

### Pulling latest changes from the Transfex

			    When adding a new language, it's resource file does not exist in the project,
			    but it's ok as it will be automatically created when pulling new translations from the service. To add a local mapping:

			    `tx set -r osm-export-tool2.master -l hr locales/hr/LC_MESSAGES/django.po`

			    or for javascript files:

			    `tx set -r osm-export-tool2.djangojs -l hr locales/hr/LC_MESSAGES/djangojs.po`


			    Once there are some translation updates, pull the latest changes for mapped resources

			    For a specific language(s):

				    `tx pull -l fr,hr`

				    For all languages:

				    `tx pull`

				    Finally, compile language files

				    `python manage.py compilemessages`


