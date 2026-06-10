from fastapi import FastAPI, Depends
from fastapi_swagger import patch_fastapi
from auth.token_auth import get_authenticated_user
from auth.basic_auth import get_current_user
from user.models import UserModel, TokenModel
from contextlib import asynccontextmanager
from tasks.routes import router as tasks_router
from user.routes import router as users_router


tags_metadata = [
    {"name": "tasks",
     "description": "Tasks API",
     "externalDocs": {
         "description": "More About Tasks",
         "url": "http://localhost:8000/tasks"
     }
     }
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application started")
    yield
    print("Application finished")


# Use patch_fastapi to enable offline Swagger docs
app = FastAPI(lifespan=lifespan, openapi_tags=tags_metadata,
              docs_url=None, swagger_ui_oauth2_swagger=None,
              title="ToDo Application",
              description="This is a Section for Description",
              version="0.0.1",
              contact={
                  "name": "Arian Ghanooni",
                  "url": "http://arianghanooni.github.io/",
                  "email": "ghanooni.ari@gmail.com",
              },
              license_info={
                "name": "MIT"
              })
patch_fastapi(app)

app.include_router(tasks_router)
app.include_router(users_router)


@app.get("/public")
def public_route():
    return {"message": "Hello, This is a Public route"}


@app.get("/private")
def private_route(user: UserModel = Depends(get_current_user)):
    print(user)
    return {"message": "Hello, This is a Private route"}


@app.get("/private_token")
def private_route(user: UserModel = Depends(get_authenticated_user)):
    print(user.username)
    return {"message": "Hello, This is a Private Token route"}