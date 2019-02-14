from google.cloud import vision

"""
    This function detects labels in give image using 
    google vision api
"""
def detect_labels(source_uri):
    
    if not source_uri:
        return None

    # Create a Cloud Vision client.
    vision_client = vision.Client()
    
    # Detect labels 
    image = vision_client.image(source_uri=source_uri)
    labels = image.detect_labels()
    result_list = []
    for label in labels:
        result_list.append(str(label.description))
    return result_list
