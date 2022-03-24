
# coding: utf-8

import pandas as pd
import re
import numbers



# #### Skriptet er en omskriving av sas-programmet
# $FELLES/sasprog/fnrsjekk.sas 
# Legger ved beskrivelse av SAS-makro
# ####

# ### SAS-makro for kontroll av fnr
# KrL 16. november 1995
# 
# SAS-makro FNRSJEKK Kontroll av fødselsnummer.
# 
# Fnrsjekk er en SAS-makro som sjekker gyldigheten til et fødselsnummer.
# Makroen har to parametre: fnr og retur. Fnr skal inneholde fødselsnummeret, mens
# retur vil inneholde en verdi som sier om fødselsnr er matematisk gyldig eller
# ikke.
# 
# Er fødselsnr matematisk gyldig, gis karaktervariabelen retur verdien 1.
# Er nummeret ugyldig gis verdien 0 når datoen er gyldig og personnummeret
# inneholder tall, og 9 hvis datoen er ugyldig eller fødselsnummeret ikke
# inneholder tall. Kontrollen returner også 0 hvis de tre første siffer i
# personnummeret (siffer 7, 8 og 9 i fødselsnr) er 000 eller 999 da disse ikke
# skal brukes.
# 
# Makroen virker slik: Først kopieres fødselsnummeret til et høyrejustert
# karakterterfelt med 11 posisjoner. Mangler fødselsnummeret ledende null i
# datoen, vil denne bli påført (midlertidig). Deretter deles feltet i ett felt
# pr. posisjon (til sammen 11 felt). Videre beregnes det første kontrollsiffer.
# Hvis dette kontrollsiffer godkjennes, beregnes det andre kontrollsifferet. Når
# begge kontrollsiffer er beregnet, sammenlignes disse med de kontrollsiffer som
# er oppgitt i fødselsnr. Er sifrene like er fødselsnr gyldig, ellers er det
# ugyldig.
# 
# Kontrollsifrene regnes ut slik:
# 
#     k1 = (s1*3) + (s2*7) + (s3*6) + s4 + (s5*8) +
#          (s6*9) + (s7*4) + (s8*5) + (s9*2)
#     r1 = rest av k1/11
# 
#     Hvis resten er 1 skal fødselsnr forkastes og er derfor ugyldig.
#     Hvis resten er 0 skal k1 også være 0
#     Hvis resten ikke er 0 eller 1 skal
#       k1 = 11 - r1;
# 
#     k2 = (s1*5) + (s2*4) + (s3*3) + (s4*2) + (s5*7) +
#          (s6*6) + (s7*5) + (s8*4) + (s9*3) + (k1*2)
#     r2 = rest av k11/11
# 
#     Hvis resten er 1 skal fødselsnr forkastes og er derfor ugyldig.
#     Hvis resten er 0 skal k11 også være 0
#     Hvis resten ikke er 0 eller 1 skal
#       k2 = 11 - r2;
# 
#    Hvis k1 = s10 og k2 = s11 er fødselsnummeret gyldig.
# 
# De variablene som brukes er lagt i temporære arrays. Dette gjør at de ikke
# blir skrevet ut til datasett. Arraynavnene er valgt slik at det skal være lite
# sannsynlig at de blir brukt som variabelnavn av brukerne.
# 
# Rutina virker ikke på SAS-versjon 6.04 (DOS-versjonen) hvis fødselsnr er
# definert numerisk. (Der er det ikke lov å bruke PUT-funksjonen på numeriske
# variable.)
# 


class Funksjoner:

  def aarhundre(self, pnr, aar):
    if '000' <= pnr <= '499':
      return aar + 1900
    elif '500' <= pnr <= '749' and aar >= 55:
      return aar + 1800
    elif '900' <= pnr <= '999' and aar >= 40:
      return aar + 1900
    elif '500' <= pnr <= '999':
      return aar + 2000
    
    return 0



  def beregn_sjekksum(self, fnr):
    """
    calculate checksum for a given national id.
    :type fnr: str
    :param fnr: Norwegian national id value
    :rtype: str
    :return:
        Returns an 11 digit national id with correct checksum values
    """
    # TODO: Kanonikalisering av fnr; må være nøyaktig 11 elementer
    # lang.
    self.s = list(fnr)
    self.idx = 9                             # Første kontrollsiffer
    for self.vekt in ((3, 7, 6, 1, 8, 9, 4, 5, 2, 1, 0),
                      (5, 4, 3, 2, 7, 6, 5, 4, 3, 2, 1)):
      self.sum = 0
      for self.x in range(11):
        # Lag vektet sum av alle siffer, utenom det
        # kontrollsifferet vi forsøker å beregne.
        if self.x != self.idx:
          self.sum = self.sum + int(self.s[self.x]) * int(self.vekt[self.x])
        
      # Kontrollsifferet har vekt 1; evt. etterfølgende
      # kontrollsiffer har vekt 0.  Riktig kontrollsiffer er det som
      # får den totale kontrollsummen (for hver vekt-serie) til å gå
      # opp i 11.
      self.kontr = (11 - (self.sum % 11)) % 11
        
      # Vi har funnet riktig siffer; sett det inn og gå videre til
      # neste.
      self.s[self.idx] = self.kontr
      self.idx += 1
    
    return "".join([str(self.x) for self.x in self.s])



  def numerisk_kontroll(self, fnr):
    """
    Checking if every position in fnr
    contains a legal number
    """
    
    self.kontroll = list(fnr)
    
    for self.n in self.kontroll:
      try:
        int(self.n)
      except:
        return 0
        
    return 1


  def strip_idnr(self, fnr):
    self.re_strip = re.compile(r"[\s\-]", re.DOTALL)
    self.nr = re.sub(self.re_strip, "", str(fnr))
    
    if len(self.nr) == 10:
      self.nr = "0" + self.nr
        
    return self.nr



  def korriger_dag_dnr(self, dag):
    #Dersom d-nummer
    if dag > 39 and dag < 80:
      dag = dag - 40
    
    return dag


  def id_sjekk(self, fnr):
    self.nr = self.strip_idnr(fnr)
    
    if len(self.nr) != 11:
        return (9)
    
    if len(self.nr) == 11: 
      if self.numerisk_kontroll(self.nr) == 0:
        return (9)

      if self.numerisk_kontroll(self.nr) == 1:
        # Del opp fødselsnummeret i dets enkelte komponenter.
        self.dag, self.mnd, self.aar, self.pnr = self.dag_mnd_aar_pnr(self.nr)
            
        #Dersom d-nummer
        self.dag = self.korriger_dag_dnr(self.dag)
            
        #Henter fire-sifret årstall
        self.yyyy = self.aarhundre(self.pnr,self.aar)

        if not self.check_for_valid_date(str(self.yyyy)+'-'+str(self.dag)+'-'+str(self.mnd)):
          return (9)
        
        if self.nr == self.beregn_sjekksum(self.nr):
        # Hvis pnr uten kontrollsiffer = 000 er fnr ugyldig
          if self.pnr == '000':
            return (0)
          else:
            return (1)           
         
        elif self.nr != self.beregn_sjekksum(self.nr):
          return (0)
    

  def dag_mnd_aar_pnr(self, nr):
    return ( int(nr[0:2]), int(nr[2:4]), int(nr[4:6]), str(nr[6:9]) )


  def fodselsdato(self, fnr):
    if self.id_sjekk(fnr) == 1:
      self.nr = self.strip_idnr(fnr)
        
      # Del opp fødselsnummeret i dets enkelte komponenter.
      self.dag, self.mnd, self.aar, self.pnr = self.dag_mnd_aar_pnr(self.nr)
        
      #Dersom d-nummer
      self.dag = self.korriger_dag_dnr(self.dag)
            
      self.yyyy = self.aarhundre(self.pnr, self.aar)

      #Vet at fdato er gyldig siden fnr er gyldig
      return str(self.dag)+'-'+str(self.mnd)+'-'+str(self.yyyy)
    
    return ''
        

  def kjonn(self, fnr):
    """
    Validate national id and check which gender flag indicates.
    """
    if self.id_sjekk(fnr) == 1:
      if isinstance(fnr, int):
        fnr = str(fnr)
        
      if int(fnr[8]) % 2:
        return 1
      else:
        return 2
       
    return 9
        

  def check_for_valid_date(self, dato):
    try:
      pd.to_datetime(dato, format="%Y-%d-%m")
      return True
 
    except:
      return False #('its not a datefield')



    



