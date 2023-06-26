from flask import Flask, request, jsonify, send_file, session, current_app
from handright import Template, handwrite
from PIL import Image, ImageFont
from threading import Thread
from PIL import Image, ImageFont, ImageQt
from dotenv import load_dotenv

load_dotenv()
import os

# import MySQLdb
import mysql.connector
from flask import g
import zipfile
import ast, io
import logging
from flask_cors import CORS
from datetime import timedelta


# 创建一个logger
logger = logging.getLogger(__name__)

# 设置日志级别
logger.setLevel(logging.DEBUG)  # 这会设置日志级别为DEBUG

# 创建 console handler，并设置级别为 ERROR
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)

# 创建 formatter
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# 把 formatter 添加到 ch
ch.setFormatter(formatter)

# 把 ch 添加到 logger
logger.addHandler(ch)

app = Flask(__name__)
CORS(app, supports_credentials=True)

app.logger.setLevel(logging.DEBUG)

SECRET_KEY = "437d75c5af744b76607fe862cf8a5a368519aca486d62c5fa69ba42c16809z88"
app.config["SECRET_KEY"] = SECRET_KEY
app.config["SESSION_COOKIE_SECURE"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "None"
app.config["MAX_CONTENT_LENGTH"] = 128 * 1024 * 1024
app.permanent_session_lifetime = timedelta(minutes=5000000)



@app.route("/api/generate_handwriting", methods=["POST"])
def generate_handwriting():
    if "username" not in session:
        return jsonify({"status": "error", "message": "You haven't login." }), 500
    try:
        data = request.form
        required_fields = [
            "text",
            "font_size",
            "line_spacing",
            "fill",
            "left_margin",
            "top_margin",
            "right_margin",
            "bottom_margin",
            "word_spacing",
            "line_spacing_sigma",
            "font_size_sigma",
            "word_spacing_sigma",
            "perturb_x_sigma",
            "perturb_y_sigma",
            "perturb_theta_sigma",
            "preview",
            "background_image",
            "font_path",
        ]
        for field in required_fields:
            if field not in data:
                return (
                    jsonify(
                        {
                            "status": "fail",
                            "message": f"Missing required field: {field}",
                        }
                    ),
                    400,
                )

        data = request.form
        print("request.form", data)
        print("request.files", request.files)
        text_to_generate = data["text"]
        if data["preview"] == "true":
            # 截短字符，只生成一面
            preview_length = 400  # 可以调整为所需的预览长度
            text_to_generate = text_to_generate[:preview_length]
        background_image = request.files["background_image"].read()
        background_image = Image.open(io.BytesIO(background_image))
        font = request.files["font_path"].read()
        font = ImageFont.truetype(io.BytesIO(font), size=int(data["font_size"]))

        template = Template(
            background=background_image,
            font=font,
            line_spacing=int(data["line_spacing"]) + int(data["font_size"]),
            fill=ast.literal_eval(data["fill"])[:3],  # Ignore the alpha value
            left_margin=int(data["left_margin"]),
            top_margin=int(data["top_margin"]),
            right_margin=int(data["right_margin"]) - int(data["word_spacing"]) * 2,
            bottom_margin=int(data["bottom_margin"]),
            word_spacing=int(data["word_spacing"]),
            line_spacing_sigma=int(data["line_spacing_sigma"]),  # 行间距随机扰动
            font_size_sigma=int(data["font_size_sigma"]),  # 字体大小随机扰动
            word_spacing_sigma=int(data["word_spacing_sigma"]),  # 字间距随机扰动
            end_chars="，。",  # 防止特定字符因排版算法的自动换行而出现在行首
            perturb_x_sigma=int(data["perturb_x_sigma"]),  # 笔画横向偏移随机扰动
            perturb_y_sigma=int(data["perturb_y_sigma"]),  # 笔画纵向偏移随机扰动
            perturb_theta_sigma=float(data["perturb_theta_sigma"]),  # 笔画旋转偏移随机扰动
        )
        images = handwrite(text_to_generate, template)
        logger.info("images generated successfully")

        # 创建一个BytesIO对象，用于保存.zip文件的内容
        zip_io = io.BytesIO()
        with zipfile.ZipFile(zip_io, "w") as zipf:
            # 遍历生成的所有图片
            for i, im in enumerate(images):
                # 使用os模块来连接路径和文件名
                image_path = os.path.join(output_path, f"{i}.png")
                im.save(image_path)
                # 将每张图片保存为一个BytesIO对象
                img_io = io.BytesIO()
                im.save(img_io, "PNG")
                img_io.seek(0)
                if data["preview"]:
                    mysql_operation(img_io)
                    return send_file(io.BytesIO(img_io.getvalue()), mimetype="image/png")
                else:
                    # 将图片BytesIO对象添加到.zip文件中
                    zipf.writestr(f"{i}.png", img_io.getvalue())
        # 将BytesIO对象的位置重置到开始
        zip_io.seek(0)
        if not data["preview"]:
            # 返回.zip文件
            mysql_operation(zip_io)
            return send_file(
                zip_io,
                attachment_filename="images.zip",
                mimetype="application/zip",
                as_attachment=True,
            )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

def mysql_operation(image_data):
    cursor = current_app.cnx.cursor()
    username = session["username"]
    # 先检查用户是否已存在
    cursor.execute("SELECT * FROM user_images WHERE username=%s", (username,))
    result = cursor.fetchone()

    # 根据查询结果来判断应该插入新纪录还是更新旧纪录
    if result is None:
        # 如果用户不存在，插入新纪录
        sql = "INSERT INTO user_images (username, image) VALUES (%s, %s)"
        params = (username, image_data)
    else:
        # 如果用户已存在，更新旧纪录
        sql = "UPDATE user_images SET image=%s WHERE username=%s"
        params = (image_data, username)
    try:
        # 执行 SQL 语句
        cursor.execute(sql, params)
        # 提交到数据库执行
        current_app.cnx.commit()
    except Exception as e:
        # 发生错误时回滚
        current_app.cnx.rollback()
        logger.info(f"An error occurred: {e}")
            
@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    logger.info(f"Received username: {username}")  # 打印接收到的用户名
    logger.info(f"Received password: {password}")  # 打印接收到的密码
    cursor = current_app.cnx.cursor()
    cursor.execute(f"SELECT password FROM user_images WHERE username=%s", (username,))
    result = cursor.fetchone()

    if result and result[0] == password:
        session.permanent = True
        session["username"] = username
        logger.info("Login success for user: {username}")
        return {"status": "success"}, 200
    else:
        logger.error("Login failed for user: {username}")
        return {
            "status": "failed",
            "message": "Login failed. Check your username and password.",
        }, 401


@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    cursor = current_app.cnx.cursor()
    cursor.execute(f"SELECT * FROM user_images WHERE username=%s", (username,))
    result = cursor.fetchone()


    if not result:
        try:
            cursor.execute(
                f"INSERT INTO user_images (username, password) VALUES (%s, %s)",
                (username, password),
            )
            current_app.cnx.commit()
            session["username"] = username
            logger.info(f"User: {username} registered successfully.")
            return jsonify(
                {
                    "status": "success",
                    "message": "Account created successfully. You can now log in.",
                }
            )
        except mysql.connector.Error as err:
            logger.error(f"Failed to insert user: {username} into DB. Error: {err}")
            return (
                jsonify(
                    {
                        "status": "fail",
                        "message": "Error occurred during registration.",
                    }
                ),
                500,
            )
    else:
        logger.error(f"Username: {username} already exists.")
        return (
            jsonify(
                {
                    "status": "fail",
                    "message": "Username already exists. Choose a different one.",
                }
            ),
            400,
        )


@app.before_request
def before_request():
    current_app.cnx = mysql.connector.connect(
        host="localhost", user="myuser", password="mypassword", database="your_database"
    )

    # current_app.cnx  = mysql.connector.connect(
    #     user='root',
    #     password=os.getenv('MYSQL_ROOT_PASSWORD'),
    #     host='127.0.0.1',
    #     database=os.getenv('MYSQL_DATABASE'))


@app.after_request
def after_request(response):
    current_app.cnx.close()
    return response


if __name__ == "__main__":
     # 获取当前路径
    current_path = os.getcwd()
    # 创建一个子文件夹用于存储输出的图片
    output_path = os.path.join(current_path, 'output')
    # 如果子文件夹不存在，就创建它
    if not os.path.exists(output_path):
        os.mkdir(output_path)
    app.run(debug=True, host="0.0.0.0")
    # good luck 6/16/2023
'''    
数据库初始化操作
'''
"""
CREATE TABLE user_images (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) UNIQUE, 
    image BLOB,
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

"""
'''
数据库结构
mysql -u root -p进入数据库
USE your_database;数据库中的一个库
describe user_images;表：
'''