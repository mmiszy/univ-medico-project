#!/bin/bash

REMOTE_DEST="mmiszy@mmiszy.webfactional.com:"
REMOTE_HOST="mmiszy.webfactional.com"
CURRENTDIR=`dirname $0`

pushd $CURRENTDIR

echo "Copying changed files to server"
# rsync --exclude="*.DS_Store" --exclude=".git" -rptlh --force --progress --delete ${CURRENTDIR}/* ${REMOTE_DEST}/
rsync -rptlh --force --progress --delete ${CURRENTDIR}/* ${REMOTE_DEST}/home/mmiszy/webapps/medica/medico/

# echo "Building on the server"
# ssh $REMOTE_HOST 'cd ~/callmanager; phing build'

popd
