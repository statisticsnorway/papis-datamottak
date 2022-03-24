from flask_mottak import db


class Leverandor(db.Model):
    kort_lev = db.Column(db.String(6), primary_key=True)
    leverandor = db.Column(db.String(100), unique=True, nullable=False)
    websak = db.Column(db.String(200), unique=False, nullable=True)
    ansv_seksjon = db.Column(db.String(3), nullable=True)
    dataleveranser = db.relationship('Dataleveranse', backref='min_leverandor',lazy=True)
    # Relasjon som ikke er synlig i basen. Kjøres i bakgrunnen.

    def __repr__(self):
        return f"Leverandor('{self.kort_lev}', '{self.leverandor}', '{self.websak}', '{self.ansv_seksjon}')"


class Dataleveranse(db.Model):
    leveranse = db.Column(db.String(100), primary_key=True)
    leverandor_kort_lev = db.Column(db.String(6), db.ForeignKey('leverandor.kort_lev'), nullable=False)
    mot_seksjon = db.Column(db.String(3), nullable=False)
    kontakt_seksjon = db.Column(db.String(120), nullable=False)
    kontaktinfo_seksjon = db.Column(db.String(120), nullable=False)
    kontakt_lev = db.Column(db.String(120), nullable=False)
    kontaktinfo_lev = db.Column(db.String(120), nullable=False)
    forventet_dato_neste = db.Column(db.String(20), nullable=False)
    hyppighet = db.Column(db.String(20), nullable=False)
    periodeleveranser = db.relationship('Periodeleveranse', backref='min_dataleveranse', lazy=True)#, foreign_keys=[leveranse])
    #leverandorer = db.relationship('Periodeleveranse', backref='leverandoren_min', lazy=True, foreign_keys=[leverandor_kort_lev])

    def __repr__(self):
        return f"Dataleveranse('{self.leveranse}', '{self.leverandor_kort_lev}', '{self.mot_seksjon}', '{self.kontakt_seksjon}')"

class Periodeleveranse(db.Model):
    periode = db.Column(db.String(20), primary_key=True)
    data_leveranse = db.Column(db.String(100), db.ForeignKey('dataleveranse.leveranse'), primary_key=True)
    kort_lev = db.Column(db.String(6), nullable=False)#db.ForeignKey('dataleveranse.leverandor_kort_lev'))
    forventet_dato = db.Column(db.String(20), nullable=False)
    mottatt_dato = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f"Periodeleveranse('{self.periode}', '{self.data_leveranse}', '{self.kort_lev}', '{self.forventet_dato}', '{self.mottatt_dato}')"