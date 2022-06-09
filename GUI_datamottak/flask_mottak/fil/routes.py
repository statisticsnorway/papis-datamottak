from os.path import isfile
import os.path
import time
from flask_mottak.config import Config
from flask import Blueprint
from flask import request, redirect, render_template, flash, url_for, json
from flask_mottak.models import Dataleveranse, Leverandor, Periodeleveranse, Kvalitet
from flask_mottak import db
from flask_mottak.models import Fil
from flask_mottak.fil.forms import SelectLeverandorForm, SelectLeveranseForm, SelectPeriodeForm, RegistrerFilSkjema,\
    fnrLeting, Konfigurasjon_mFnrLeting, Konfigurasjon_uFnrLeting
from flask_mottak.main.utils import read_sas_file
import pandas as pd
import pyreadstat
import os
import random


fil = Blueprint('fil', __name__)

with open('config_sas.json', 'r') as myfile:
    data = json.loads(myfile.read())

@fil.route('/fil')
def filer():
    filer = Fil.query.all()

    return filer[0].__repr__()


@fil.route('/fil_leverandor', methods=['POST', 'GET'])
def velg_leverandor():
    alle_kortnavn = [kn.kort_lev for kn in db.session.query(Leverandor.kort_lev).all()]

    form = SelectLeverandorForm()
    form.kort_lev.choices = [kn for kn in alle_kortnavn]

    if form.validate_on_submit():
        kort_lev = form.kort_lev.data

        return redirect(url_for('fil.velg_leveranse', kort_lev=kort_lev))

    return render_template('velg_dataleverandor.html', title='Filmottak', form=form, legend='Filmottak')


@fil.route('/fil_leveranse/<string:kort_lev>', methods=['POST', 'GET'])
def velg_leveranse(kort_lev):
    leveranser = Dataleveranse.query.filter_by(kort_lev=kort_lev).all()
    alle_leveranser = [lev.leveranse for lev in leveranser]
    leverandor = Leverandor.query.get(kort_lev)
    min_leverandor = leverandor.kort_lev

    form = SelectLeveranseForm()
    form.leveranse.choices = [lev for lev in alle_leveranser]
    if len(alle_leveranser) == 0:
        flash(f'Ingen dataleveranse er knyttet til dataleverandøren {kort_lev}', 'info')

    if form.validate_on_submit():
        kort_lev = form.kort_lev.data
        leveranse = form.leveranse.data

        return redirect(url_for('fil.velg_periodeleveranse', kort_lev=kort_lev, leveranse=leveranse))

    elif request.method == 'GET':
        form.kort_lev.data = kort_lev
        form.kort_lev(disabled=True)


    return render_template('velg_dataleveranse.html', title='Dataleveranse', form=form, leveranse=min_leverandor, legend='Dataleveranser')



@fil.route('/fil_periodeleveranse/<string:kort_lev>/<string:leveranse>', methods=['POST', 'GET'])
def velg_periodeleveranse(kort_lev, leveranse):
    periodeleveranser = Periodeleveranse.query.filter_by(leveranse=leveranse)
    alle_periodeleveranser = [pl.periode for pl in periodeleveranser]


    form = SelectPeriodeForm()
    form.periode.choices = [plv for plv in alle_periodeleveranser]
    if len(alle_periodeleveranser) == 0:
        flash(f'Ingen periodeleveranse er knyttet til dataleveransen {leveranse}', 'info')

    if form.validate_on_submit():
        leveranse = form.leveranse.data
        periode = form.periode.data

        return redirect(url_for('fil.registrerFil', kort_lev=kort_lev, leveranse=leveranse, periode=periode))

    elif request.method == 'GET':
        form.kort_lev.data = kort_lev
        form.kort_lev(disabled=True)
        form.leveranse.data = leveranse
        form.leveranse(disabled=True)

    return render_template('velg_periodeleveranse.html', title='Periodeleveranser', form=form, kort_lev=kort_lev, dataleveranse=leveranse, legend='Periodeleveranser')



@fil.route('/filer/<string:kort_lev>/<string:periode>/<string:leveranse>/registrer', methods=['POST', 'GET'])
def registrerFil(kort_lev, periode, leveranse):
    periodeleveransen = Periodeleveranse.query.get([periode, leveranse, kort_lev])

    #Kodet som benyttes under testing slik at en kan jobbe med samme objekt flere ganger
    db.session.query(Kvalitet).delete()
    db.session.query(Fil).delete()
    db.session.commit()

    form = RegistrerFilSkjema()

    if form.validate_on_submit():
        if isfile(form.filnavn.data):
            if os.access(form.filnavn.data, os.R_OK):
                filtype = form.filnavn.data.rsplit('.', 1)[1].lower()
                if filtype in Config.EXTENSIONS:
                    flash(f'{form.filnavn.data} er en gyldig fil', 'info')

                    fil = Fil(periode=form.periode.data, leveranse=form.data_leveranse.data,
                                           kort_lev=form.kort_lev.data, filnavn=form.filnavn.data,
                                           fil_mottatt=form.fil_mottatt.data)
                    #periodeleveransen.append(fil)
                    db.session.add(fil)
                    db.session.commit()
                    flash(f'Fil opprettet for {form.periode.data} - {form.data_leveranse.data} - {form.filnavn.data}, {fil}!',
                          'success')
                    configfil = data['innfil']
                    # NB! Programmet /ssb/stamme01/papis/_Programmer/SAS/oppstartsprogram.sas forventer at en
                    # oppgir filsti på ETT høyere nivå enn der selve filen ligger.
                    # Jeg ønsker at en får sjekket at en faktisk peker på en reell fil.
                    # Fjerner derfor siste ledd i stien etter sjekk. Vurder endring av sas-program.
                    stamme = form.filnavn.data.rsplit('/', 1)[0]
                    configfil['sti'] = stamme.rsplit('/', 1)[0] + '/'
                    configfil['navn'] = form.filnavn.data.rsplit('/', 1)[1].rsplit('.', 1)[0]#.lower()
                    configfil['filtype'] = filtype
                    configfil['dataleverandor'] = form.kort_lev.data
                    configfil['leveranse'] = form.data_leveranse.data
                    configfil['aargang'] = form.periode.data

                    return redirect(url_for('fil.fnr_leting', kort_lev=kort_lev, leveranse=leveranse, filnavn=form.filnavn.data))
                else:
                    flash(f'Kun følgende filtyper kan behandles: {Config.EXTENSIONS}. Fil oppgitt: {form.filnavn.data}', 'warning')

            else:
                flash(f'Ikke tilgang til {form.filnavn.data}', 'warning')
        else:
            flash(f'{form.filnavn.data} er ikke en gyldig fil', 'warning')

        return redirect(url_for('fil.registrerFil', kort_lev=kort_lev, leveranse=leveranse, periode=periode))

    elif request.method == 'GET':
        form.data_leveranse.data = leveranse
        form.data_leveranse(disabled=True)
        form.periode.data = periode
        form.periode(disabled=True)
        form.kort_lev.data = kort_lev

    return render_template('filbeskrivelse.html', title='Registrer fil',
                           form=form, legend='Registrer fil')


#@fil.route('/filvalg/<path:filnavn>', methods=['POST', 'GET'])
#def filvalg(filnavn):
#    form = HentFilSkjema()

#    if form.validate_on_submit():
        #Vurder å flytte selve innlesingen til et senere steg
        #df = read_sas_file('/'+filnavn)
#        df = read_sas_file(filnavn)
#        header = df.columns.tolist()
#        row = df.iloc[0].values.tolist()

       # if form.til_alder < form.fra_alder:
       #     flash(f'Til alder - {form.til_alder.data} må være høyere enn fra alder - {form.fra_alder.data}', 'warning')
       #     return redirect(url_for('fil.filvalg', filnavn=fil.filnavn))

       # else:
#        return redirect(url_for('fil.fnr_leting', filnavn=filnavn, header=header, row=row))

#    elif request.method == 'GET':
#        form.filnavn.data = filnavn
#        form.tidbef.data = 'g2021m09d30'
#        form.fodselsnr.data = 'fnr'
#        #form.fnrleting.data = '1'


#    return render_template('filnavn.html', title='Filvalg', form=form, legend='Filvalg')


@fil.route('/fnr_leting/<string:kort_lev>/<string:leveranse>/<path:filnavn>', methods=['POST', 'GET'])
def fnr_leting(kort_lev, leveranse, filnavn):
    form = fnrLeting()

    if form.validate_on_submit():
        if form.fnrleting.data == 'Ja':
            configfil = data['fnrlet']
            configfil['fnrleting'] = '1'

            return redirect(url_for('fil.letingFnr', kort_lev=kort_lev, leveranse=leveranse, filnavn=filnavn))

        else:
            configfil = data['fnrlet']
            configfil['fnrleting'] = '0'

            return redirect(url_for('fil.uten_letingFnr', kort_lev=kort_lev, leveranse=leveranse, filnavn=filnavn))

    return render_template('fnrleting.html', title='Filvalg', form=form, legend='Filvalg')


@fil.route('/fnr_leting/skjema/<string:kort_lev>/<string:leveranse>/<path:filnavn>', methods=['POST', 'GET'])
def letingFnr(kort_lev, leveranse, filnavn):

    df, meta = pyreadstat.read_sas7bdat('/'+filnavn, metadataonly=True)
    meta_a = sorted(meta.variable_storage_width.items(), key=lambda x: x[1], reverse=True)

    fnr_liste = []
    liste = []
    for k, v in meta_a:
        if v == 11:
            fnr_liste.append(k)
        else:
            liste.append(k)

    variabel_liste = fnr_liste + liste


    form = Konfigurasjon_mFnrLeting()
    form.pseudo_vars.choices = [("---")] + [var for var in variabel_liste]
    form.fodselsnr.choices = [("---")]+[var for var in variabel_liste]
    form.fornavn.choices = [("---")]+[var for var in variabel_liste]
    form.mellomnavn.choices = [("---")]+[var for var in variabel_liste]
    form.etternavn.choices = [("---")]+[var for var in variabel_liste]

    if form.validate_on_submit():
        pseudo_vars = form.pseudo_vars.data
        fodselsnr = form.fodselsnr.data
        fornavn = form.fornavn.data if form.fornavn.data != '---' else ''
        mellomnavn = form.mellomnavn.data if form.mellomnavn.data != '---' else ''
        etternavn = form.etternavn.data if form.etternavn.data != '---' else ''
        fra_alder = form.fra_alder.data
        til_alder = form.til_alder.data
        tidbef = form.tidbef.data
        sep = form.sep.data
        header = form.header.data
        innlprog = form.innlprog.data
        bruk_navn = form.bruk_navn.data
        filstamme = form.filstamme.data

        fnrlet_configfil = data['fnrlet']
        fnrlet_configfil['fodselsnr'] = fodselsnr
        fnrlet_configfil['fornavn'] = fornavn
        fnrlet_configfil['mellomnavn'] = mellomnavn
        fnrlet_configfil['etternavn'] = etternavn
        fnrlet_configfil['fra_alder'] = fra_alder
        fnrlet_configfil['til_alder'] = til_alder
        fnrlet_configfil['tidbef'] = tidbef

        innfil_configfil = data['innfil']
        innfil_configfil['sep'] = sep
        innfil_configfil['header'] = header
        innfil_configfil['innlprog'] = innlprog
        innfil_configfil['bruk_navn'] = bruk_navn
        innfil_configfil['filstamme'] = filstamme

        flash(f'Konfigurasjonsfil: {data}', 'info')
        flash(f'Variable som skal pseudonymiseres: {pseudo_vars}', 'info')

        #sas-program som kjører fnr-leting og kontroller forventer et løpenummer på config-fila
        number = random.randint(1000, 9999)

        configfil = "/ssb/stamme01/papis/Oppstart/config_sas_"+str(number)+".json"
        with open(configfil, 'w') as f:
            json.dump(data, f, indent=4)

        fd = os.open(configfil, os.O_RDWR)
        mode = 0o777
        os.fchmod(fd, mode)
        #os.chmod(configfil, os.stat.S_IROTH | os.stat.S_IWOTH | os.stat.S_IXOTH)

        return redirect(url_for('fil.kvalitetsrapport', number=number, kort_lev=kort_lev, leveranse=leveranse))


    return render_template('konfig_mFnrLeting.html', title='Konfigurer fnrleting',
                           form=form, legend='Konfigurer fnrleting')


@fil.route('/utenFnr_leting/skjema/<string:kort_lev>/<string:leveranse>/<path:filnavn>', methods=['POST', 'GET'])
def uten_letingFnr(kort_lev, leveranse, filnavn):
    df, meta = pyreadstat.read_sas7bdat('/'+filnavn, metadataonly=True)
    meta_a = sorted(meta.variable_storage_width.items(), key=lambda x: x[1], reverse=True)

    fnr_liste = []
    liste = []
    for k, v in meta_a:
        if v == 11:
            fnr_liste.append(k)
        else:
            liste.append(k)

    variabel_liste = fnr_liste + liste

    form = Konfigurasjon_uFnrLeting()
    form.fodselsnr.choices = [("---")]+[var for var in variabel_liste]
    form.pseudo_vars.choices = [("---")]+[var for var in variabel_liste]

    if form.validate_on_submit():
        pseudo_vars = form.pseudo_vars.data
        fodselsnr = form.fodselsnr.data
        sep = form.sep.data
        header = form.header.data
        innlprog = form.innlprog.data
        bruk_navn = form.bruk_navn.data
        filstamme = form.filstamme.data

        fnrlet_configfil = data['fnrlet']
        fnrlet_configfil['fodselsnr'] = fodselsnr
        innfil_configfil = data['innfil']
        innfil_configfil['sep'] = sep
        innfil_configfil['header'] = header
        innfil_configfil['innlprog'] = innlprog
        innfil_configfil['bruk_navn'] = bruk_navn
        innfil_configfil['filstamme'] = filstamme

        flash(f'Konfigurasjonsfil: {data}', 'info')
        flash(f'Variable som skal pseudonymiseres: {pseudo_vars}', 'info')

        # sas-program som kjører fnr-leting og kontroller forventer et løpenummer på config-fila
        number = random.randint(1000, 9999)

        configfil = "/ssb/stamme01/papis/Oppstart/config_sas_" + str(number) + ".json"
        with open(configfil, 'w') as f:
            json.dump(data, f, indent=4)

        fd = os.open(configfil, os.O_RDWR)
        mode = 0o777
        os.fchmod(fd, mode)
        #os.chmod(configfil, os.stat.S_IROTH | os.stat.S_IWOTH | os.stat.S_IXOTH)

        return redirect(url_for('fil.kvalitetsrapport_utenFnrLeting', number=number, kort_lev=kort_lev, leveranse=leveranse))

    return render_template('konfig_uFnrLeting.html', title='Konfigurer fil for kontroll',
                           form=form, legend='Konfigurer fil for kontroll')


@fil.route('/kvalitetsrapport/<string:number>/<string:kort_lev>/<string:leveranse>', methods=['POST', 'GET'])
def kvalitetsrapport(number, kort_lev, leveranse):#leveranse
    loggfil = '/ssb/stamme01/papis/wk12/loggfil_'+number+'.sas7bdat'

    while not os.path.exists(loggfil):
        time.sleep(1)

    if os.path.isfile(loggfil):
        try:
            df = pd.read_sas(loggfil, format='sas7bdat', index=None,
                         encoding='unicode_escape', iterator=False)

        except OSError:
            flash(f'Får ikke lest: {loggfil} !',
                  'warning')
    else:
        flash(f'Ikke en gyldig fil: {loggfil} !',
              'warning')

    #df = pd.read_sas('/ssb/stamme01/papis/wk12/loggfil_9999.sas7bdat', encoding='latin1')


    df.loc[df['verdi'].str.strip() == '.', 'verdi'] = None
    variabler = df['variabel'].tolist()
    verdi = df['verdi'].tolist()
    var_verdi = dict(zip(variabler, verdi))

    rapport = Kvalitet(periode = var_verdi['periode'], leveranse = leveranse, kort_lev = kort_lev,
        filnavn = var_verdi['Filsti'] + '1_Raadata/' + var_verdi['filnavn_inn'] + '.' + var_verdi['Filtype'], lenke_rapp = "Test",
        behandlet_datotid = var_verdi['behandlet_datotid'], antall_obs = var_verdi['antall_obs'],
        antall_unike_id = var_verdi['antall_unike_id'], antall_gyldige_id = var_verdi['antall_gyldige_id'],
        antall_gyldige_fnr = var_verdi['antall_gyldige_fnr'], antall_gyldige_dnr = var_verdi['antall_gyldige_dnr'],
        antall_gyld_fnr_lik = var_verdi['antall_gyld_fnr_lik'], antall_gyld_fnr_ulik = var_verdi['antall_gyld_fnr_ulik'],
        antall_gyld_dnr_lik = var_verdi['antall_gyld_dnr_lik'], antall_gyld_dnr_ulik = var_verdi['antall_gyld_dnr_ulik'],
        antall_ugyldige = var_verdi['antall_ugyldige'], feil_1e_1 = var_verdi["feil_1e_1"] ,
        feil_1e_2 = var_verdi["feil_1e_2"], feil_1f_1 = var_verdi["feil_1f_1"], feil_1f_2 = var_verdi["feil_1f_2"],
        feil_2a_1 = var_verdi["feil_2a_1"], feil_2a_2 = var_verdi["feil_2a_2"], feil_2a_3 = var_verdi["feil_2a_3"],
        feil_2a_4 = var_verdi["feil_2a_4"], feil_2a_5 = var_verdi["feil_2a_5"], feil_2a_6 = var_verdi["feil_2a_6"],
        feil_2b_1 = var_verdi["feil_2b_1"], feil_2b_2 = var_verdi["feil_2b_2"], feil_2b_3 = var_verdi["feil_2b_3"],
        feil_2b_4 = var_verdi["feil_2b_4"], feil_2b_5 = var_verdi["feil_2b_5"], feil_2b_6 = var_verdi["feil_2b_6"],
        feil_2c_1 = var_verdi["feil_2c_1"], feil_2c_2 = var_verdi["feil_2c_2"], feil_2d_1 = var_verdi["feil_2d_1"],
        feil_2d_2 = var_verdi["feil_2d_2"], feil_2d_3 = var_verdi["feil_2d_3"], feil_2e = var_verdi["feil_2e"],
        feil_2f_1 = var_verdi["feil_2f_1"], feil_2f_2 = var_verdi["feil_2f_2"], feil_2f_3 = var_verdi["feil_2f_3"],
        feil_2g = var_verdi["feil_2g"], fnr_leting = var_verdi["fnr_leting"], t1_antall_id = var_verdi["t1_antall_id"],
        t11_ant_koblet_fnr = var_verdi["t11_ant_koblet_fnr"], t11_ant_feil_a1 = var_verdi["t11_ant_feil_a1"],
        t11_ant_feil_a2 = var_verdi["t11_ant_feil_a2"], t11_ant_feil_a3 = var_verdi["t11_ant_feil_a3"],
        t11_ant_feil_a4 = var_verdi["t11_ant_feil_a4"], t11_ant_feil_a5 = var_verdi["t11_ant_feil_a5"],
        t11_ant_feil_a6 = var_verdi["t11_ant_feil_a6"], t11_ant_feil_b1 = var_verdi["t11_ant_feil_b1"],
        t11_ant_feil_b2 = var_verdi["t11_ant_feil_b2"], t11_ant_feil_b3 = var_verdi["t11_ant_feil_b3"],
        t11_ant_feil_b4 = var_verdi["t11_ant_feil_b4"], t11_ant_feil_b5 = var_verdi["t11_ant_feil_b5"],
        t11_ant_feil_b6 = var_verdi["t11_ant_feil_b6"], t11_ant_feil_c1 = var_verdi["t11_ant_feil_c1"],
        t11_ant_feil_c2 = var_verdi["t11_ant_feil_c2"], t11_ant_feil_andre = var_verdi["t11_ant_feil_andre"],
        t11_ant_ikke_kobl = var_verdi["t11_ant_ikke_kobl"], t12_antall_id = var_verdi["t12_antall_id"],
        t12_ant_koblet_dnr = var_verdi["t12_ant_koblet_dnr"], t12_ant_feil_a1 = var_verdi["t12_ant_feil_a1"],
        t12_ant_feil_a2 = var_verdi["t12_ant_feil_a2"], t12_ant_feil_a3 = var_verdi["t12_ant_feil_a3"],
        t12_ant_feil_a4 = var_verdi["t12_ant_feil_a4"], t12_ant_feil_a5 = var_verdi["t12_ant_feil_a5"],
        t12_ant_feil_a6 = var_verdi["t12_ant_feil_a6"], t12_ant_feil_b1 = var_verdi["t12_ant_feil_b1"],
        t12_ant_feil_b2 = var_verdi["t12_ant_feil_b2"], t12_ant_feil_b3 = var_verdi["t12_ant_feil_b3"],
        t12_ant_feil_b4 = var_verdi["t12_ant_feil_b4"], t12_ant_feil_b5 = var_verdi["t12_ant_feil_b5"],
        t12_ant_feil_b6 = var_verdi["t12_ant_feil_b6"], t12_ant_feil_c1 = var_verdi["t12_ant_feil_c1"],
        t12_ant_feil_c2 = var_verdi["t12_ant_feil_c2"], t12_ant_feil_andre = var_verdi["t12_ant_feil_andre"],
        t12_ant_ikke_kobl = var_verdi["t12_ant_ikke_kobl"], t13_ant_paa_fil = var_verdi["t13_ant_paa_fil"],
        t13_ant_fnr_koblet = var_verdi["t13_ant_fnr_koblet"], t13_ant_dnr_koblet = var_verdi["t13_ant_dnr_koblet"],
        t13_ant_koblet_fnr_lik = var_verdi["t13_ant_koblet_fnr_lik"], t13_ant_koblet_fnr_ulik = var_verdi["t13_ant_koblet_fnr_ulik"],
        t13_ant_koblet_dnr_lik = var_verdi["t13_ant_koblet_dnr_lik"], t13_ant_koblet_dnr_ulik = var_verdi["t13_ant_koblet_dnr_ulik"],
        t1_ant_koblet = var_verdi["t1_ant_koblet"], t1_ant_ikke_koblet = var_verdi["t1_ant_ikke_koblet"],
        t2_antall_id = var_verdi["t2_antall_id"], t21_ant_koblet_fnr = var_verdi["t21_ant_koblet_fnr"],
        t21_ant_feil_a1 = var_verdi["t21_ant_feil_a1"], t21_ant_feil_a2 = var_verdi["t21_ant_feil_a2"],
        t21_ant_feil_a3 = var_verdi["t21_ant_feil_a3"], t21_ant_feil_a4 = var_verdi["t21_ant_feil_a4"],
        t21_ant_feil_a5 = var_verdi["t21_ant_feil_a5"], t21_ant_feil_a6 = var_verdi["t21_ant_feil_a6"],
        t21_ant_feil_b1 = var_verdi["t21_ant_feil_b1"], t21_ant_feil_b2 = var_verdi["t21_ant_feil_b2"],
        t21_ant_feil_b3 = var_verdi["t21_ant_feil_b3"], t21_ant_feil_b4 = var_verdi["t21_ant_feil_b4"],
        t21_ant_feil_b5 = var_verdi["t21_ant_feil_b5"], t21_ant_feil_b6 = var_verdi["t21_ant_feil_b6"],
        t21_ant_feil_c1 = var_verdi["t21_ant_feil_c1"], t21_ant_feil_c2 = var_verdi["t21_ant_feil_c2"],
        t21_ant_feil_andre = var_verdi["t21_ant_feil_andre"], t21_ant_ikke_kobl = var_verdi["t21_ant_ikke_kobl"],
        t22_antall_id = var_verdi["t22_antall_id"], t22_ant_koblet_dnr = var_verdi["t22_ant_koblet_dnr"],
        t22_ant_feil_a1 = var_verdi["t22_ant_feil_a1"], t22_ant_feil_a2 = var_verdi["t22_ant_feil_a2"],
        t22_ant_feil_a3 = var_verdi["t22_ant_feil_a3"], t22_ant_feil_a4 = var_verdi["t22_ant_feil_a4"],
        t22_ant_feil_a5 = var_verdi["t22_ant_feil_a5"], t22_ant_feil_a6 = var_verdi["t22_ant_feil_a6"],
        t22_ant_feil_b1 = var_verdi["t22_ant_feil_b1"], t22_ant_feil_b2 = var_verdi["t22_ant_feil_b2"],
        t22_ant_feil_b3 = var_verdi["t22_ant_feil_b3"], t22_ant_feil_b4 = var_verdi["t22_ant_feil_b4"],
        t22_ant_feil_b5 = var_verdi["t22_ant_feil_b5"], t22_ant_feil_b6 = var_verdi["t22_ant_feil_b6"],
        t22_ant_feil_c1 = var_verdi["t22_ant_feil_c1"], t22_ant_feil_c2 = var_verdi["t22_ant_feil_c2"],
        t22_ant_feil_andre = var_verdi["t22_ant_feil_andre"], t22_ant_ikke_kobl = var_verdi["t22_ant_ikke_kobl"],
        t23_ant_paa_fil = var_verdi["t23_ant_paa_fil"], t23_ant_fnr_koblet = var_verdi["t23_ant_fnr_koblet"],
        t23_ant_dnr_koblet = var_verdi["t23_ant_dnr_koblet"], t23_ant_koblet_fnr_lik = var_verdi["t23_ant_koblet_fnr_lik"],
        t23_ant_koblet_fnr_ulik = var_verdi["t23_ant_koblet_fnr_ulik"], t23_ant_koblet_dnr_lik = var_verdi["t23_ant_koblet_dnr_lik"],
        t23_ant_koblet_dnr_ulik = var_verdi["t23_ant_koblet_dnr_ulik"], t2_ant_koblet = var_verdi["t2_ant_koblet"],
        t2_ant_ikke_koblet = var_verdi["t2_ant_ikke_koblet"], t2_ant_avvist = var_verdi["t2_ant_avvist"],
        t3_antall_id = var_verdi["t3_antall_id"], t31_ant_koblet_fnr = var_verdi["t31_ant_koblet_fnr"],
        t31_ant_feil_a1 = var_verdi["t31_ant_feil_a1"], t31_ant_feil_a2 = var_verdi["t31_ant_feil_a2"],
        t31_ant_feil_a3 = var_verdi["t31_ant_feil_a3"], t31_ant_feil_a4 = var_verdi["t31_ant_feil_a4"],
        t31_ant_feil_a5 = var_verdi["t31_ant_feil_a5"], t31_ant_feil_a6 = var_verdi["t31_ant_feil_a6"],
        t31_ant_feil_b1 = var_verdi["t31_ant_feil_b1"], t31_ant_feil_b2 = var_verdi["t31_ant_feil_b2"],
        t31_ant_feil_b3 = var_verdi["t31_ant_feil_b3"], t31_ant_feil_b4 = var_verdi["t31_ant_feil_b4"],
        t31_ant_feil_b5 = var_verdi["t31_ant_feil_b5"], t31_ant_feil_b6 = var_verdi["t31_ant_feil_b6"],
        t31_ant_feil_c1 = var_verdi["t31_ant_feil_c1"], t31_ant_feil_c2 = var_verdi["t31_ant_feil_c2"],
        t31_ant_feil_andre = var_verdi["t31_ant_feil_andre"], t31_ant_ikke_kobl = var_verdi["t31_ant_ikke_kobl"],
        t32_antall_id = var_verdi["t32_antall_id"], t32_ant_koblet_dnr = var_verdi["t32_ant_koblet_dnr"],
        t32_ant_feil_a1 = var_verdi["t32_ant_feil_a1"], t32_ant_feil_a2 = var_verdi["t32_ant_feil_a2"],
        t32_ant_feil_a3 = var_verdi["t32_ant_feil_a3"], t32_ant_feil_a4 = var_verdi["t32_ant_feil_a4"],
        t32_ant_feil_a5 = var_verdi["t32_ant_feil_a5"], t32_ant_feil_a6 = var_verdi["t32_ant_feil_a6"],
        t32_ant_feil_b1 = var_verdi["t32_ant_feil_b1"], t32_ant_feil_b2 = var_verdi["t32_ant_feil_b2"],
        t32_ant_feil_b3 = var_verdi["t32_ant_feil_b3"], t32_ant_feil_b4 = var_verdi["t32_ant_feil_b4"],
        t32_ant_feil_b5 = var_verdi["t32_ant_feil_b5"],
                       t32_ant_feil_b6 = var_verdi['t32_ant_feil_b6'],
        t32_ant_feil_c1 = var_verdi["t32_ant_feil_c1"], t32_ant_feil_c2 = var_verdi["t32_ant_feil_c2"],
        t32_ant_feil_andre = var_verdi["t32_ant_feil_andre"], t32_ant_ikke_kobl = var_verdi["t32_ant_ikke_kobl"],
        t33_ant_paa_fil = var_verdi["t33_ant_paa_fil"], t33_ant_fnr_koblet = var_verdi["t33_ant_fnr_koblet"],
        t33_ant_dnr_koblet = var_verdi["t33_ant_dnr_koblet"], t33_ant_koblet_fnr_lik = var_verdi["t33_ant_koblet_fnr_lik"],
        t33_ant_koblet_fnr_ulik = var_verdi["t33_ant_koblet_fnr_ulik"], t33_ant_koblet_dnr_lik = var_verdi["t33_ant_koblet_dnr_lik"],
        t33_ant_koblet_dnr_ulik = var_verdi["t33_ant_koblet_dnr_ulik"], t3_ant_koblet = var_verdi["t3_ant_koblet"],
        t3_ant_ikke_koblet = var_verdi["t3_ant_ikke_koblet"], t4_antall_id = var_verdi["t4_antall_id"],
        t41_ant_koblet = var_verdi["t41_ant_koblet"], t41_ant_feil_a1 = var_verdi["t41_ant_feil_a1"],
        t41_ant_feil_a2 = var_verdi["t41_ant_feil_a2"], t41_ant_feil_a3 = var_verdi["t41_ant_feil_a3"],
        t41_ant_feil_a4 = var_verdi["t41_ant_feil_a4"], t41_ant_feil_a5 = var_verdi["t41_ant_feil_a5"],
        t41_ant_feil_a6 = var_verdi["t41_ant_feil_a6"], t41_ant_feil_b1 = var_verdi["t41_ant_feil_b1"],
        t41_ant_feil_b2 = var_verdi["t41_ant_feil_b2"], t41_ant_feil_b3 = var_verdi["t41_ant_feil_b3"],
        t41_ant_feil_b4 = var_verdi["t41_ant_feil_b4"], t41_ant_feil_b5 = var_verdi["t41_ant_feil_b5"],
        t41_ant_feil_b6 = var_verdi["t41_ant_feil_b6"], t41_ant_feil_c1 = var_verdi["t41_ant_feil_c1"],
        t41_ant_feil_c2 = var_verdi["t41_ant_feil_c2"], t41_ant_feil_e = var_verdi["t41_ant_feil_e"],
        t41_ant_feil_f1 = var_verdi["t41_ant_feil_f1"], t41_ant_feil_f2 = var_verdi["t41_ant_feil_f2"],
        t41_ant_feil_f3 = var_verdi["t41_ant_feil_f3"], t41_ant_feil_andre = var_verdi["t41_ant_feil_andre"],
        t41_ant_ikke_kobl = var_verdi["t41_ant_ikke_kobl"], t43_ant_paa_fil = var_verdi["t43_ant_paa_fil"],
        t43_ant_fnr_koblet = var_verdi["t43_ant_fnr_koblet"], t43_ant_dnr_koblet = var_verdi["t43_ant_dnr_koblet"],
        t43_ant_koblet_fnr_lik = var_verdi["t43_ant_koblet_fnr_lik"], t43_ant_koblet_fnr_ulik = var_verdi["t43_ant_koblet_fnr_ulik"],
        t43_ant_koblet_dnr_lik = var_verdi["t43_ant_koblet_dnr_lik"], t43_ant_koblet_dnr_ulik = var_verdi["t43_ant_koblet_dnr_ulik"],
        t4_ant_koblet = var_verdi["t4_ant_koblet"], t4_ant_ikke_koblet = var_verdi["t4_ant_ikke_koblet"],
        t5_antall_id = var_verdi["t5_antall_id"], t51_ant_koblet = var_verdi["t51_ant_koblet"],
        t51_ant_feil_a1 = var_verdi["t51_ant_feil_a1"], t51_ant_feil_a2 = var_verdi["t51_ant_feil_a2"],
        t51_ant_feil_a3 = var_verdi["t51_ant_feil_a3"], t51_ant_feil_a4 = var_verdi["t51_ant_feil_a4"],
        t51_ant_feil_a5 = var_verdi["t51_ant_feil_a5"], t51_ant_feil_a6 = var_verdi["t51_ant_feil_a6"],
        t51_ant_feil_b1 = var_verdi["t51_ant_feil_b1"], t51_ant_feil_b2 = var_verdi["t51_ant_feil_b2"],
        t51_ant_feil_b3 = var_verdi["t51_ant_feil_b3"], t51_ant_feil_b4 = var_verdi["t51_ant_feil_b4"],
        t51_ant_feil_b5 = var_verdi["t51_ant_feil_b5"], t51_ant_feil_b6 = var_verdi["t51_ant_feil_b6"],
        t51_ant_feil_c1 = var_verdi["t51_ant_feil_c1"], t51_ant_feil_c2 = var_verdi["t51_ant_feil_c2"],
        t51_ant_feil_e = var_verdi["t51_ant_feil_e"], t51_ant_feil_f1 = var_verdi["t51_ant_feil_f1"],
        t51_ant_feil_f2 = var_verdi["t51_ant_feil_f2"], t51_ant_feil_f3 = var_verdi["t51_ant_feil_f3"],
        t51_ant_feil_andre = var_verdi["t51_ant_feil_andre"], t51_ant_ikke_kobl = var_verdi["t51_ant_ikke_kobl"],
        t53_ant_paa_fil = var_verdi["t53_ant_paa_fil"], t53_ant_fnr_koblet = var_verdi["t53_ant_fnr_koblet"],
        t53_ant_dnr_koblet = var_verdi["t53_ant_dnr_koblet"], t53_ant_koblet_fnr_lik = var_verdi["t53_ant_koblet_fnr_lik"],
        t53_ant_koblet_fnr_ulik = var_verdi["t53_ant_koblet_fnr_ulik"], t53_ant_koblet_dnr_lik = var_verdi["t53_ant_koblet_dnr_lik"],
        t53_ant_koblet_dnr_ulik = var_verdi["t53_ant_koblet_dnr_ulik"], t5_ant_koblet = var_verdi["t5_ant_koblet"],
        t5_ant_ikke_koblet = var_verdi["t5_ant_ikke_koblet"])

    db.session.add(rapport)
    db.session.commit()

    flash(f'Rapport laget for: {loggfil} !',
          'info')
    #flash(f'Kvalitetsrapport opprettet for {rapport.__repr__()} !',
    #      'success')
    #flash(f'Kvalitetsrapport opprettet for {var_verdi["filnavn_inn"] + "." + var_verdi["Filtype"]} !',
     #     'success')

    return render_template('kvalitetsrapport.html',  title='Kvalitetsrapport', legend='kvalitetsrapport')#logg=rapport,


@fil.route('/kvalitetsrapport_utenFnrLeting/<string:number>/<string:kort_lev>/<string:leveranse>', methods=['POST', 'GET'])
def kvalitetsrapport_utenFnrLeting(number, kort_lev, leveranse):#leveranse
    loggfil = '/ssb/stamme01/papis/wk12/loggfil_'+number+'.sas7bdat'

    while not os.path.exists(loggfil):
        time.sleep(1)

    if os.path.isfile(loggfil):
        try:
            df = pd.read_sas(loggfil, format='sas7bdat', index=None,
                         encoding='unicode_escape', iterator=False)

        except OSError:
            flash(f'Får ikke lest: {loggfil} !',
                  'warning')
    else:
        flash(f'Ikke en gyldig fil: {loggfil} !',
              'warning')

    #df = pd.read_sas('/ssb/stamme01/papis/wk12/loggfil_9999.sas7bdat', encoding='latin1')


    df.loc[df['verdi'].str.strip() == '.', 'verdi'] = None
    variabler = df['variabel'].tolist()
    verdi = df['verdi'].tolist()
    var_verdi = dict(zip(variabler, verdi))

    rapport = Kvalitet(periode = var_verdi['periode'], leveranse = leveranse, kort_lev = kort_lev,
        filnavn = var_verdi['Filsti'] + '1_Raadata/' + var_verdi['filnavn_inn'] + '.' + var_verdi['Filtype'], lenke_rapp = "Test",
        behandlet_datotid = var_verdi['behandlet_datotid'], antall_obs = var_verdi['antall_obs'],
        antall_unike_id = var_verdi['antall_unike_id'], antall_gyldige_id = var_verdi['antall_gyldige_id'],
        antall_gyldige_fnr = var_verdi['antall_gyldige_fnr'], antall_gyldige_dnr = var_verdi['antall_gyldige_dnr'],
        antall_gyld_fnr_lik = var_verdi['antall_gyld_fnr_lik'], antall_gyld_fnr_ulik = var_verdi['antall_gyld_fnr_ulik'],
        antall_gyld_dnr_lik = var_verdi['antall_gyld_dnr_lik'], antall_gyld_dnr_ulik = var_verdi['antall_gyld_dnr_ulik'],
        antall_ugyldige = var_verdi['antall_ugyldige'], feil_1e_1 = var_verdi["feil_1e_1"] ,
        feil_1e_2 = var_verdi["feil_1e_2"], feil_1f_1 = var_verdi["feil_1f_1"], feil_1f_2 = var_verdi["feil_1f_2"],
        feil_2a_1 = var_verdi["feil_2a_1"], feil_2a_2 = var_verdi["feil_2a_2"], feil_2a_3 = var_verdi["feil_2a_3"],
        feil_2a_4 = var_verdi["feil_2a_4"], feil_2a_5 = var_verdi["feil_2a_5"], feil_2a_6 = var_verdi["feil_2a_6"],
        feil_2b_1 = var_verdi["feil_2b_1"], feil_2b_2 = var_verdi["feil_2b_2"], feil_2b_3 = var_verdi["feil_2b_3"],
        feil_2b_4 = var_verdi["feil_2b_4"], feil_2b_5 = var_verdi["feil_2b_5"], feil_2b_6 = var_verdi["feil_2b_6"],
        feil_2c_1 = var_verdi["feil_2c_1"], feil_2c_2 = var_verdi["feil_2c_2"], feil_2d_1 = var_verdi["feil_2d_1"],
        feil_2d_2 = var_verdi["feil_2d_2"], feil_2d_3 = var_verdi["feil_2d_3"], feil_2e = var_verdi["feil_2e"],
        feil_2f_1 = var_verdi["feil_2f_1"], feil_2f_2 = var_verdi["feil_2f_2"], feil_2f_3 = var_verdi["feil_2f_3"],
        feil_2g = var_verdi["feil_2g"], fnr_leting = var_verdi["fnr_leting"])

    db.session.add(rapport)
    db.session.commit()

    flash(f'Rapport laget for: {loggfil} !',
          'info')
    #flash(f'Kvalitetsrapport opprettet for {rapport.__repr__()} !',
    #      'success')
    #flash(f'Kvalitetsrapport opprettet for {var_verdi["filnavn_inn"] + "." + var_verdi["Filtype"]} !',
     #     'success')

    return render_template('kvalitetsrapport.html',  title='Kvalitetsrapport', legend='kvalitetsrapport')#logg=rapport,