Face Recognition API
--------------------

FastAPI meets face_recognition.


Running
-------

First, we need to train yoloair model. 
Default values should suffice.

forgetful uses yoloair to identify objects, and when people are found it uses
face_recognition with knn to search in a postgresql-based faces database.

.. code:: bash

        poetry run yoloair_train
        DBURI="postgresql://postgres:pass@localhost/postgres" poetry run uvicorn app:app


Then you can have a look at the OpenAPI interface on https://localhost:8080/

It currently exports two endpoints, one for loading new faces into the model
and one for checking for a face match.

You can easily import faces into the model via curl with:

.. code:: bash

   curl -X 'POST' "http://localhost:8000/faces/add/$name" \
       -H 'accept: application/json' \
       -H 'Content-Type: multipart/form-data' \
       -F "face_image=@$image;type=image/jpeg"

And you can identify objects via curl with:

.. code:: bash

        curl -X 'POST' \
          'http://localhost:8000/recognize/' \
          -H 'accept: application/json' \
          -H 'Content-Type: multipart/form-data' \
          -F 'face_image=@your_image.jpg;type=image/webp'

Docker
------

This software comes dockerized at https://dockerhub.com/XayOn/forgetful.

You can run it with:

.. code:: bash

        docker run XayOn/forgetful -p 8080:8080 -e DBURI="postgresql://postgres:pass@localhost/postgres" 
