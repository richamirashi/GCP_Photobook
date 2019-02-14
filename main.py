# [START app]
import os
import uuid
import logging
from datetime import datetime

from gvision import detect_labels

from flask import Flask, redirect, render_template, request

from google.cloud import datastore
from google.cloud import storage

# Clobal Variables
CLOUD_STORAGE_BUCKET = os.environ.get('CLOUD_STORAGE_BUCKET')

# The kind for the new entity.
KIND = 'PhotoBook'


# Flask Application
app = Flask(__name__)


@app.route('/')
def view_all():
    # Create a Cloud Datastore client.
    datastore_client = datastore.Client()

    # Use the Cloud Datastore client to fetch information from Datastore about each photo.
    query = datastore_client.query(kind=KIND)
    image_entities = list(query.fetch())

    # Return a Jinja2 HTML template and pass in image_entities as a parameter.
    return render_template('view_all.html', image_entities=image_entities)

@app.route('/categories/<category_name>')
def categories_view(category_name):
    # Create a Cloud Datastore client.
    datastore_client = datastore.Client()

    # Use the Cloud Datastore client to fetch information from Datastore about each photo.
    query = datastore_client.query(kind=KIND)
    image_entities = list(query.fetch())

    result_list = []
    people_synonyms = ['man','women','girl', 'boy']
    all_values = ['people', 'animal', 'flower'] 
    values_to_check = []
    if category_name in all_values:
        values_to_check.append(category_name)
        if category_name == 'people':
            values_to_check.extend(people_synonyms)
    
        for entity in image_entities:
            for name in values_to_check: 
                if name in entity['labels'].lower():
                    result_list.append(entity)
                    break
    else:  # For other
        values_to_check.extend(all_values) 
        values_to_check.extend(people_synonyms) 
        for entity in image_entities:
            flag = True
            for name in values_to_check: 
                if name in entity['labels'].lower():
                    flag = False
                    break
            if flag:
                result_list.append(entity)
    

    # Return a Jinja2 HTML template and pass in image_entities as a parameter.
    return render_template('view_all.html', image_entities=result_list)


def upload_to_cloud_storage(photo):
    # Create a Cloud Storage client.
    storage_client = storage.Client()

    # Get the bucket that the file will be uploaded to.
    bucket = storage_client.get_bucket(CLOUD_STORAGE_BUCKET)

    # Create a new blob and upload the file's content.
    uuid_name = str(uuid.uuid4()).replace('-','')
    blob = bucket.blob(uuid_name)
    blob.upload_from_string(
            photo.read(), content_type=photo.content_type)

    # Make the blob publicly viewable.
    blob.make_public()

    # Use the Cloud Vision client to detect labels.
    source_uri = 'https://storage.googleapis.com/{}/{}'.format(CLOUD_STORAGE_BUCKET, blob.name)
    labels = detect_labels(source_uri)
    
    # Return data
    return blob, labels

# Uploads and adds all the details of the photo and redirects to the home page
@app.route('/upload_photo', methods=['GET', 'POST'])
def upload_photo():

    # Upload photo
    photo = request.files['file']
    blob, labels = upload_to_cloud_storage(photo) 
    
    # Create a Cloud Datastore client.
    datastore_client = datastore.Client()

    # The name/ID for the new entity.
    name = blob.name

    # Create the Cloud Datastore key for the new entity.
    key = datastore_client.key(KIND, name)

    # Construct the new entity using the key. Set dictionary values for entity
    # keys blob_name, storage_public_url, timestamp, and joy.
    entity = datastore.Entity(key)
    entity['name'] = request.form['name']
    entity['location'] = request.form['location']
    entity['timestamp'] = request.form['timestamp']
    entity['blob_name'] = blob.name
    entity['image_public_url'] = blob.public_url
    entity['labels'] = '{}, {}'.format(','.join(labels), request.form['labels'])

    # Save the new entity to Datastore.
    datastore_client.put(entity)

    # Redirect to the home page.
    return redirect('/')

# Navigates to the upload.html page to add and upload the photo
@app.route('/upload.html')
def upload():
    # Return a Jinja2 HTML template.
    return render_template('upload.html')

# Navigates to the edit.html page and pre loads data from datastore
@app.route('/edit/<id>')
def pre_edit(id):
    # Create a Cloud Datastore client.
    datastore_client = datastore.Client()

    # Use the Cloud Datastore client to fetch information about the photo.
    key = datastore_client.key(KIND, id)
    entity = datastore_client.get(key)
    
    # Return a Jinja2 HTML template.
    return render_template('edit.html', entity=entity)

# Uppdted the photo details, and the navigates to home page.
@app.route('/post_edit/<id>', methods=['GET', 'POST'])
def post_edit(id):
    # Create a Cloud Datastore client.
    datastore_client = datastore.Client()

    # set data
    key = datastore_client.key(KIND, id)
    entity = datastore_client.get(key)
    entity['name'] = request.form['name']
    entity['location'] = request.form['location']
    entity['timestamp'] = request.form['timestamp']
    entity['labels'] = request.form['labels']
    
    # Upload photo
    if request.files['file']:
        photo = request.files['file']
        blob, labels = upload_to_cloud_storage(photo) 
        entity['image_public_url'] = blob.public_url
        entity['labels'] = ','.join(labels)

    # Update data
    datastore_client.put(entity)
    
    # Redirect to the home page.
    return redirect('/')


# Delete photo.
@app.route('/delete/<id>')
def delete(id):
    # Create a Cloud Datastore client.
    datastore_client = datastore.Client()

    # Get data handler
    key = datastore_client.key(KIND, id)
    
    # Delete
    datastore_client.delete(key)
    
    # Redirect to the home page.
    return redirect('/')


@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500


if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [END app]
