from flask_mottak import create_app

app = create_app()

if __name__ == "__main__":
    print('Navigate to http://10.32.10.70:5050/')
    app.run(host='0.0.0.0',port=5050,debug=True,threaded=True)

    
