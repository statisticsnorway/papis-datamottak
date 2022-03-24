from flask_pseudo import create_app

app = create_app()


if __name__ == "__main__":
    #app.run(debug=True, threaded=True)
    #app.run(host='0.0.0.0', debug=True)
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
    
