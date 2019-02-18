# GCP_Photobook

The Photobook is a web application that runs on the [Google Cloud Platform (GCP)](https://cloud.google.com/) to manage
and automatically label the images in the photobook.

![photobook](https://github.com/richamirashi/GCP_Photobook/blob/master/static/img/photobook.JPG)

The web interface has following features:
- **Upload a photo:** The user types in the metadata of a photo (name of the photographer, location of the photo, and date of the photo taken) and then uploads the image. After a photo is uploaded, the [Google’s Cloud Vision API](https://cloud.google.com/vision/) labels each photo. Such labels are then used
to organize the photobook into four categories:
  - animals
  - flowers
  - people
  - others
- **My photobook:** Displays uploaded photos in the above four categories.
- **Manage photos:** The user edits a photo’s metadata, replaces the photo with a new photo, manually corrects a photo’s category given by the Vision API, or removes a photo from the photobook.

## Framework:

- [Google App Engine](https://cloud.google.com/appengine/) as a datastore
- [Google Cloud Storage](https://cloud.google.com/storage/) for storing unstructured data such as images in this case
- [Python](https://www.python.org/)
- [Flask framework](http://flask.pocoo.org/)
- [Google’s Cloud Vision API](https://cloud.google.com/vision/)
