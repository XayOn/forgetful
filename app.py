from decimal import Decimal
import math
import os

import numpy as np
from pydantic import BaseModel
import sqlalchemy
from sqlalchemy.dialects.postgresql import ARRAY

import databases
from face_recognition import face_encodings, load_image_file, face_locations
from fastapi import FastAPI, UploadFile, HTTPException
from loguru import logger
from sklearn import neighbors

DBURI = str(os.getenv('DBURI'))
database = databases.Database(DBURI)

metadata = sqlalchemy.MetaData()

persons = sqlalchemy.Table(
    "person", metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, index=True),
    sqlalchemy.Column("name", sqlalchemy.String),
    sqlalchemy.Column("image", ARRAY(sqlalchemy.Text)))

engine = sqlalchemy.create_engine(DBURI)
metadata.create_all(engine)
app = FastAPI()
CLASSIFIER = None


class PersonResponse(BaseModel):
    name: str


async def load_model():
    res = {
        person["name"]: person["image"]
        async for person in database.iterate(persons.select())
    }
    if n_neighbors := os.getenv('n_neighbors'):
        n_neighbors = int(n_neighbors)
    else:
        n_neighbors = int(round(math.sqrt(len(res.keys()))))

    knn_clf = neighbors.KNeighborsClassifier(n_neighbors=n_neighbors,
                                             algorithm='ball_tree',
                                             weights='distance')

    if not res:
        logger.debug('no source data provided')
        return

    logger.debug(f'Loading {len(res.keys())} persons')
    try:
        knn_clf.fit([[np.float64(b) for b in a] for a in res.values()],
                    list(res.keys()))
        logger.debug('initialized model')
        global CLASSIFIER
        CLASSIFIER = knn_clf
    except Exception:
        logger.exception('Cound not init model')


@app.on_event("startup")
async def startup():
    logger.debug('connecting to database')
    await database.connect()
    logger.debug('initializing model')
    await load_model()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


def get_faces_encodings(face_image):
    face = load_image_file(face_image.file)
    facelocs = face_locations(face)
    if len(facelocs) == 0:
        raise HTTPException(status_code=404, detail="No faces found")
    return facelocs, face_encodings(face, known_face_locations=facelocs)


@app.post("/faces/search/", response_model=PersonResponse)
async def search(face_image: UploadFile):
    if not CLASSIFIER:
        return {'error': 'app_starting_up'}
    knn_clf = CLASSIFIER
    face_locs, faces_encodings = get_faces_encodings(face_image)
    closest = knn_clf.kneighbors(faces_encodings, n_neighbors=1)
    are_matches = [closest[0][i][0] <= 0.6 for i in range(len(face_locs))]
    preds = zip(knn_clf.predict(faces_encodings), are_matches)
    try:
        return dict(name=next(pred for pred, rec in preds if rec))
    except StopIteration as e:
        raise HTTPException(status_code=404, detail="None recognized") from e


@app.post("/faces/add/{name}", response_model=PersonResponse)
async def add(name: str, face_image: UploadFile):
    faces_encodings, _ = get_faces_encodings(face_image)
    image = [str(Decimal(a)) for a in faces_encodings[0]]
    query = persons.insert().values(name=name, image=image)
    last_record_id = await database.execute(query)
    await load_model()
    return dict(name=name, id=last_record_id)
