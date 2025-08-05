from django import forms

posiciones = [
    ('1', 'PG - Base'),
    ('2', 'SG - Escolta'),
    ('3', 'SF - Alero'),
    ('4', 'PF - Ala-Pívot'),
    ('5', 'C - Pívot')
]

edades = [(str(i), str(i)) for i in range(18, 41)]
juegos = [(str(i), str(i)) for i in range(60, 83)]  # 60–82 partidos

class PlayerStatsForm(forms.Form):
    Age = forms.ChoiceField(label="Edad", choices=edades)
    Pos = forms.ChoiceField(label="Posición", choices=posiciones)
    G = forms.ChoiceField(label="Partidos Jugados (60-82)", choices=juegos)

    MP = forms.FloatField(label="Minutos Promedio")
    P2 = forms.FloatField(label="Tiros de 2P encestados")
    P2A = forms.FloatField(label="Tiros de 2P intentados (≥ 2P)")
    P3 = forms.FloatField(label="Tiros de 3P encestados")
    P3A = forms.FloatField(label="Tiros de 3P intentados (≥ 3P)")
    FT = forms.FloatField(label="Tiros libres encestados")
    FTA = forms.FloatField(label="Tiros libres intentados (≥ FT)")
    ORB = forms.FloatField(label="Rebotes ofensivos")
    DRB = forms.FloatField(label="Rebotes defensivos")
    AST = forms.FloatField(label="Asistencias")
    STL = forms.FloatField(label="Robos")
    BLK = forms.FloatField(label="Bloqueos")
    TOV = forms.FloatField(label="Pérdidas de balón")
    PF = forms.FloatField(label="Faltas personales (0.1 – 6)")

    def clean_PF(self):
        pf = self.cleaned_data["PF"]
        if pf < 0.1 or pf > 6:
            raise forms.ValidationError("Las faltas personales deben estar entre 0.1 y 6.")
        return pf
