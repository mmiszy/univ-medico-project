#!/bin/bash

REMOTE_DEST="mmiszy@mmiszy.webfactional.com:"
REMOTE_HOST="mmiszy@mmiszy.webfactional.com"
CURRENTDIR=`dirname $0`

pushd $CURRENTDIR

echo "Copying changed files to server"
# rsync --exclude="*.DS_Store" --exclude=".git" -rptlh --force --progress --delete ${CURRENTDIR}/* ${REMOTE_DEST}/
rsync -rptlh --force --progress --delete --exclude="static" ${CURRENTDIR}/* ${REMOTE_DEST}/home/mmiszy/webapps/medica/medico/
rsync -rptlh --force --progress --delete ${CURRENTDIR}/static/* ${REMOTE_DEST}/home/mmiszy/webapps/static_media/

if [[ $1 == "restart" ]]; then
	#statements
	echo "Restarting apache"
	ssh ${REMOTE_HOST} '/home/mmiszy/webapps/medica/apache2/bin/restart'
fi

popd
