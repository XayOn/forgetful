Face Recognition API
--------------------

FastAPI meets face_recognition.


Running
-------

.. code:: 

        DBURI="postgresql://postgres@localhost/postgres" poetry run uvicorn app:app


Then you can have a look at the OpenAPI interface on https://localhost:8080/

It currently exports two endpoints, one for loading new faces into the model
and one for checking for a face match
