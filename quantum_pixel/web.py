#cSpell:ignore stegano jsonable
"""Website with fastapi"""
import shutil
import uuid
import os
import time
import asyncio
import json
from concurrent.futures.thread import ThreadPoolExecutor
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from PIL import Image, UnidentifiedImageError

from . import Generator, Steganography


PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.path.join(PROJECT_ROOT, "static", "images")
os.makedirs(IMAGE_DIR, exist_ok=True)


async def cleanup_worker():
    """For every 1 hour, delete uploaded files with lifespan of 1 hour. This prevent everything."""
    try:
        while True:
            try:
                for name in os.listdir(IMAGE_DIR):
                    path = os.path.join(IMAGE_DIR, name)
                    if time.time() - os.path.getmtime(path) > 3600:
                        try:
                            os.remove(path)
                        except IsADirectoryError:
                            shutil.rmtree(path)
            except FileNotFoundError:
                pass
            await asyncio.sleep(3600)
    except asyncio.CancelledError:
        return

@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Lifespan of the app, on event startup and shutdown."""
    # startup event.
    asyncio.create_task(cleanup_worker())
    yield
    # Shutdown event.
    executor.shutdown(cancel_futures=True)
    for name in os.listdir(IMAGE_DIR):
        path = os.path.join(IMAGE_DIR, name)
        try:
            os.remove(path)
        except IsADirectoryError:
            shutil.rmtree(path)

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["POST"],
    max_age=100,
)
app.mount("/static", StaticFiles(directory=os.path.join(PROJECT_ROOT, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(PROJECT_ROOT, "templates"))
executor = ThreadPoolExecutor()
background_task: dict = {}

def _remove_from_list(uid: str):
    background_task.pop(uid, None)

def _join_uid(uid: str, filename: str) -> str:
    return os.path.join(IMAGE_DIR, uid, filename)



### ------------------------ Welcome to my shit ------------------------------------



@app.get("/", response_class=HTMLResponse)
async def start(request: Request):
    """A default start on app."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/", response_class=RedirectResponse)
async def upload(request: Request):
    """Upload the file, then encode or decode depend on selection."""
    form = await request.form()
    file = form.get("file")

    if not file or not form.get("upload_type"):
        return templates.TemplateResponse("index.html",
                                          {"request": request, "error": "Unable to load form."})

    # Im poor u know lol. You can delete this line, just acknowledge your cpu power.
    if file.size > 1_073_741_824:
        return templates.TemplateResponse("index.html",
                                          {"request": request, "error": "File should be <1GB."})

    while True: # Guarantee an individualized uid.
        uid = uuid.uuid4().hex
        try:
            os.mkdir(os.path.join(IMAGE_DIR, uid))
            break
        except FileExistsError:
            continue

    upload_type = form.get("upload_type")
    with open(_join_uid(uid, f"{upload_type}_input.png"), "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return RedirectResponse(f"/{upload_type}/{uid}", status_code=303)

@app.get("/encode/{uid}", response_class=HTMLResponse)
async def start_encode(request: Request, uid: str):
    """Start the encode html."""
    if not os.path.exists(_join_uid(uid, "encode_input.png")):
        return templates.TemplateResponse("encode.html", {"request": request,
                "error": templates.get_template("error.html").render({"error":
                    ("The image file cannot be found, you might just exit and got auto cleanup! "
                    "Otherwise, there might be an attack/error, please issue me if that's so.")})})
    return templates.TemplateResponse("encode.html", {"request": request, "uid": uid})

@app.post("/encode/{uid}")
async def end_encode(request: Request, uid: str):
    """This guy here gonna cook us dinner."""
    input_path = _join_uid(uid, "encode_input.png")
    if not os.path.exists(input_path):
        return JSONResponse(content={
            "error": templates.get_template("error.html").render({"error":
                    ("The image file cannot be found, you might just exit and got auto cleanup! "
                    "Otherwise, there might be an attack/error, please issue me if that's so.")})
        })

    form = await request.form()
    match form.get("selected"):
        case "panel_preview":
            if input_path and form.get("intensity"):
                try:
                    future_item = asyncio.get_event_loop().run_in_executor(executor,
                                    Generator(input_path).preview, float(form.get("intensity")),
                                    _join_uid(uid, "encode_preview.png"))
                    future_item.add_done_callback(lambda _: _remove_from_list(uid))
                    background_task.update({uid: future_item})

                    async def _progress_streaming():
                        for progress in await future_item:
                            yield f"{progress}\n"
                        yield json.dumps({"result": templates.get_template("result.html")
                                        .render({"path": f"{uid}/encode_preview.png",
                                                 "download": "encode-preview",})})
                    return StreamingResponse(_progress_streaming(), media_type="text/plain")

                except asyncio.exceptions.CancelledError:
                    return_error = "User exited."
                except AssertionError as err:
                    return_error = err

        case "panel_resize":
            if input_path and form.get("image") and form.get("width") and form.get("length"):
                Image.open(form.get("image").file)\
                            .resize((int(form.get("width")), int(form.get("length"))))\
                            .save(_join_uid(uid, "encode_resize.png"), optimize=True)
                return JSONResponse(content={
                        "result": templates.get_template("result.html").render({
                            "path": f"{uid}/encode_resize.png",
                            "download": "encode-resize",
                        })})

        case "panel_steganography":
            if input_path and form.get("disguise"):
                Image.open(form.get("disguise").file)\
                            .save(_join_uid(uid, "encode_disguise.png"), optimize=True)
                future_item=asyncio.get_event_loop().run_in_executor(executor, Steganography.encode,
                                                        form.get("password"), input_path,
                                                        _join_uid(uid, "encode_steganography.png"),
                                                        _join_uid(uid, "encode_disguise.png"))
                future_item.add_done_callback(lambda _: _remove_from_list(uid))
                background_task.update({uid: future_item})

                try:
                    if await future_item:
                        return_error = future_item.result()
                    else:
                        return JSONResponse(content={
                        "result": templates.get_template("result.html").render({
                            "path": f"{uid}/encode_steganography.png",
                            "download": "encode-steganography",
                        })})
                except asyncio.exceptions.CancelledError:
                    return_error = "User exited."

        case _:
            return_error = "Unable to load form."
    return JSONResponse(content=({
        "error": templates.get_template("error.html").render({"error": return_error})
    }))


@app.get("/decode/{uid}", response_class=HTMLResponse)
async def start_decode(request: Request, uid: str):
    """Start the decode html."""
    if not os.path.exists(_join_uid(uid, "decode_input.png")):
        return templates.TemplateResponse("decode.html", {"request": request,
                "error": templates.get_template("error.html").render({"error":
                    ("The image file cannot be found, you might just exit and got auto cleanup! "
                    "Otherwise, there might be an attack/error, please issue me if that's so.")})})
    return templates.TemplateResponse("decode.html", {"request": request})

@app.post("/decode/{uid}", response_class=JSONResponse)
async def end_decode(request: Request, uid: str):
    """And this guys serve it with fire."""
    if not os.path.exists(_join_uid(uid, "decode_input.png")):
        return JSONResponse(content={
            "error": templates.get_template("error.html").render({"error":
                    ("The image file cannot be found, you might just exit and got auto cleanup! "
                    "Otherwise, there might be an attack/error, please issue me if that's so.")})
        })

    form = await request.form()
    input_path = _join_uid(uid, "decode_input.png")
    output_folder = _join_uid(uid, "decode_output")

    try:
        os.mkdir(output_folder)
    except FileExistsError:
        pass

    future_item = asyncio.get_event_loop().run_in_executor(executor, Steganography.decode,
                                        form.get("password"), input_path, output_folder)
    future_item.add_done_callback(lambda _: _remove_from_list(uid))
    background_task.update({uid: future_item})

    try:
        if await future_item:
            return_error = "Invalid password, maybe ask the author's permission?"\
                            if future_item.result() == "Decryption error" else future_item
        else:
            for dirpath, _, filenames in os.walk(output_folder):
                for filename in filenames:
                    try:
                        Image.open(os.path.join(dirpath, filename))
                        return JSONResponse(content=
                            {"result":templates.get_template("result.html").render({
                                "path": f"{uid}/decode_output/{filename}",
                                "download": "decode-output"
                            })})
                    except UnidentifiedImageError:
                        continue
            return_error = "There is no readable image within the encoded file."
    except asyncio.exceptions.CancelledError:
        return_error = "User exited."
    except BaseException as err: #pylint: disable=W0718:broad-exception-caught
        return_error = f"This error usually occurs when the image is not encoded from here: {err}"
    return {"error": templates.get_template("error.html").render({"error": return_error})}

@app.post("/remove/{uid}")
async def remove(uid: str):
    """Remove file when user exit."""    
    shutil.rmtree(os.path.join(IMAGE_DIR, uid), ignore_errors=True)
    task = background_task.get(uid)
    if task:
        task.cancel()
