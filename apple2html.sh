#!/bin/sh

# grab news
python apple2html.py

TODAY=`date +'%Y-%m-%d'`
TODAY_FOLDER=public_html/$TODAY
cd public_html && tar cf $TODAY.tar $TODAY
# ALL_HTLM=($TODAY_FOLDER/*.html)

# convert them into pdf with wkhtmltopdf
# for f in ${ALL_HTLM[@]}
# do
    # FN=`basename $f`
    # NON_EXTENSION=`echo $FN | awk -F. '{print $1}'`
    # echo "wkhtmltopdf -s A6 $f $TODAY_FOLDER/${TODAY}_${NON_EXTENSION}.pdf"
    # wkhtmltopdf -s A6 $f $TODAY_FOLDER/${TODAY}_${NON_EXTENSION}.pdf
# done

# zip -9 $TODAY_FOLDER/${TODAY}.zip $TODAY_FOLDER/*.pdf
# send_to_kindle.py $TODAY_FOLDER/${TODAY}.zip
