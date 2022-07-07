from flask_mottak import create_app, db

app = create_app()
app.pseudoService.start()
db.create_all(app=create_app())
app.app_context().push()
#db.session.commit()

#with app.app_context():
#    db.create_all()
#    db.create_all(app=create_app())
#    db.session.commit()

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5000,debug=True,threaded=True)

    
