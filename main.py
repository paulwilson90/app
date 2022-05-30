import json
import math
import re
import time
from threading import Thread
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen

class HomeScreen(Screen):
    pass
class CalcScreen(Screen):
    pass

GUI = Builder.load_file("main.kv")
class MainApp(App):
    def build(self):
        return GUI

    def on_start(self):
        self.remove_rwy_buttons()

    def remove_rwy_buttons(self):
        rwy1 = self.root.ids['calc_screen'].ids['rwy1']
        rwy2 = self.root.ids['calc_screen'].ids['rwy2']
        rwy3 = self.root.ids['calc_screen'].ids['rwy3']
        rwy4 = self.root.ids['calc_screen'].ids['rwy4']
        rwy5 = self.root.ids['calc_screen'].ids['rwy5']
        rwy6 = self.root.ids['calc_screen'].ids['rwy6']
        self.root.ids['calc_screen'].remove_widget(rwy1)
        self.root.ids['calc_screen'].remove_widget(rwy2)
        self.root.ids['calc_screen'].remove_widget(rwy3)
        self.root.ids['calc_screen'].remove_widget(rwy4)
        self.root.ids['calc_screen'].remove_widget(rwy5)
        self.root.ids['calc_screen'].remove_widget(rwy6)

    def enable_button(self):
        runway_ = self.root.ids['calc_screen'].ids['runway_'].text
        ldg_wt_ = self.root.ids['calc_screen'].ids['ldg_wt_'].text
        flap_ = self.root.ids['calc_screen'].ids['flap_'].text
        wind_ = self.root.ids['calc_screen'].ids['wind_'].text
        vapp_add_ = self.root.ids['calc_screen'].ids['vapp_add_'].text
        reduced_np_ = self.root.ids['calc_screen'].ids['reduced_np_'].text
        ref_speeds_ = self.root.ids['calc_screen'].ids['ref_speeds_'].text
        wet_dry_ = self.root.ids['calc_screen'].ids['wet_dry_'].text

        go_button = self.root.ids['calc_screen'].ids['go_button']
        if runway_ and ldg_wt_ and flap_ and vapp_add_ and reduced_np_ and ref_speeds_ and wet_dry_:
            go_button.disabled = False
        else:
            go_button.disabled = True

    def vapp_vref_txt(self):
        vapp_add = self.root.ids['calc_screen'].ids['vapp_add']
        if vapp_add.text == '0':
            self.root.ids['calc_screen'].ids['_vapp_add'].text = "[b][color=#3E9933]VAPP = VREF[/color][/b]"
        else:
            self.root.ids['calc_screen'].ids['_vapp_add'].text = "[b][color=#3E9933]VREF + " + vapp_add.text + '[/color][/b]'

    def lda_txt(self, airport, runway):
        with open('airport_data.json') as ap_data:
            ap = json.load(ap_data)
        runway_data = ap[airport][runway]
        airport_elevation = runway_data["Elev"]
        runway_length = runway_data["Length"]
        self.root.ids['calc_screen'].ids['lda_txt'].text = "[b][u][color=#F9AF25]LDA IS " + runway_length + "m[/color" \
                                                                                                            "][/u][/b] "

    def ldr_txt(self, ldr):
        lda = re.search(r'\d{4}m', self.root.ids['calc_screen'].ids['lda_txt'].text).group()[:-1]
        if int(lda) < int(ldr):
            colour = 'FF3D16'  # red
            self.thread()
        else:
            colour = '3E9933'  # green
        self.root.ids['calc_screen'].ids['ldr_txt'].text = f"[b][u][color=#{colour}]LDR IS " + ldr + "m[/color][/u][/b]"

    def thread(self):
        p3 = Thread(target=lambda: self.flashing_ldr())
        p3.start()

    def flashing_ldr(self):
        op = 1
        for r in range(7):
            self.root.ids['calc_screen'].ids['ldr_txt'].opacity = op
            if op == 1:
                op -= 1
            else:
                op += 1
            time.sleep(.3)

    def change_screen(self, screen_name):
        # get the screen manager from the main.kv file
        screen_manager = self.root.ids['screen_manager']
        screen_manager.current = screen_name

    def runway_buttons(self, airport):
        with open('airport_data.json') as ap_data:
            ap = json.load(ap_data)
        airport_data = ap[airport]
        f = 0
        for runway in airport_data:
            f += 1
            rwy_ = "rwy" + str(f)
            rwy_num = self.root.ids['calc_screen'].ids[rwy_]
            self.root.ids['calc_screen'].add_widget(rwy_num)
            self.root.ids['calc_screen'].ids[rwy_].children[0].text = str(runway)

    def store_units(self):
        airport = self.root.ids['home_screen'].ids['dest1'].text
        runway = self.root.ids['calc_screen'].ids['runway_'].text
        weight = self.root.ids['calc_screen'].ids['ldg_wt_'].text
        flap = self.root.ids['calc_screen'].ids['flap_'].text
        wind_comp = self.root.ids['calc_screen'].ids['wind_'].text
        vapp_add = self.root.ids['calc_screen'].ids['vapp_add_'].text
        reduced_np = self.root.ids['calc_screen'].ids['reduced_np_'].text
        ref_speeds = self.root.ids['calc_screen'].ids['ref_speeds_'].text
        wet_dry = self.root.ids['calc_screen'].ids['wet_dry_'].text
        self.get_landing_dist(airport, runway, weight, flap, wind_comp, vapp_add, reduced_np, ref_speeds, wet_dry)


    def get_landing_dist(self, airport, runway, weight, flap, wind_comp, vapp_add, reduced_np, ref_speeds, wet_dry):
        wind_digits = re.search(r'\d*', wind_comp).group()
        if wind_comp == '':
            wind_digits = '0'
            wind_comp = '0'
            upper_wind_comp = '0'
            lower_wind_comp = '0'
        else:
            if wind_digits == '0':
                wind_comp = '0'
                upper_wind_comp = '0'
                lower_wind_comp = '0'
            else:
                if 'HEADWIND' in wind_comp:
                    wind_comp = re.search(r'\d*', wind_comp).group() + 'h'
                    upper_wind_comp = str((math.ceil(int(wind_comp[:-1]) / 10)) * 10) + 'h'
                    if upper_wind_comp == '0h':
                        upper_wind_comp = '0'
                    lower_wind_comp = str((math.floor(int(wind_comp[:-1]) / 10)) * 10) + 'h'
                    if lower_wind_comp == '0h':
                        lower_wind_comp = '0'
                else:
                    wind_comp = re.search(r'\d*', wind_comp).group() + 't'
                    upper_wind_comp = str((math.ceil(int(wind_comp[:-1]) / 10)) * 10) + 't'
                    if upper_wind_comp == '0t':
                        upper_wind_comp = '0'
                    lower_wind_comp = str((math.floor(int(wind_comp[:-1]) / 10)) * 10) + 't'
                    if lower_wind_comp == '0t':
                        lower_wind_comp = '0'
        flap = flap[-2:]
        weight = str(float(re.search(r'\d*', weight).group()) / 1000)
        wt_up = str(math.ceil(float(weight)))
        wt_down = str(math.floor(float(weight)))
        with open('airport_data.json') as ap_data:
            lda_elev = json.load(ap_data)
        rwy_data = lda_elev[airport][runway]
        LDA = rwy_data['Length']
        elev = rwy_data['Elev']
        elev = int(elev) / 1000

        print(LDA, elev)

        with open('ulds.json') as ulds:
            uld_ = json.load(ulds)
        up = math.ceil(elev)
        down = math.floor(elev)
        # interpolating with the upper weight of the two elevation figures
        wt_up_up_data = uld_[flap][wt_up][up]
        wt_up_dwn_data = uld_[flap][wt_up][down]
        uld_up_wt = round(wt_up_dwn_data + ((wt_up_up_data - wt_up_dwn_data) * (elev - down)))
        # interpolating with the lower weight of the two elevation figures
        wt_dwn_up_data = uld_[flap][wt_down][up]
        wt_dwn_dwn_data = uld_[flap][wt_down][down]
        uld_dwn_wt = round(wt_dwn_dwn_data + ((wt_dwn_up_data - wt_dwn_dwn_data) * (elev - down)))
        # interpolating for weight between the two elevation interpolated figures
        final_uld = round(uld_dwn_wt + (uld_up_wt - uld_dwn_wt) * (float(weight) - int(wt_down)))
        print(final_uld, "Final ULD")

        with open('winds.json') as winds:
            ap = json.load(winds)
        if flap == "35" or flap == "15":
            uld_index = (final_uld - 700) / 25
        else:
            uld_index = ((final_uld - 700) / 25) - 1
        up_2 = math.ceil(uld_index)
        down_2 = math.floor(uld_index)
        # interpolating with the upper wind index of the two uld figures
        wind_up_up_data = ap[flap][upper_wind_comp][up_2]
        wind_up_dwn_data = ap[flap][upper_wind_comp][down_2]
        wind_up_corrected_wind_slope = round(
            wind_up_dwn_data + ((wind_up_up_data - wind_up_dwn_data) * (uld_index - down_2)))
        # interpolating with the lower wind index of the two uld figures
        wind_down_up_data = ap[flap][lower_wind_comp][up_2]
        wind_down_dwn_data = ap[flap][lower_wind_comp][down_2]
        wind_down_corrected_wind_slope = round(
            wind_down_dwn_data + ((wind_down_up_data - wind_down_dwn_data) * (uld_index - down_2)))
        final_wind_correct = round(
            wind_down_corrected_wind_slope + (wind_up_corrected_wind_slope - wind_down_corrected_wind_slope) * (
                        int(wind_digits) / 10))
        print(final_wind_correct, "before additives")

        vapp_percent_add = 0
        for kt in range(int(vapp_add)):
            vapp_percent_add += 0.02
        final_ldr = final_wind_correct * (1 + vapp_percent_add)
        if reduced_np == 'REDUCED NP':
            final_ldr = final_ldr * 1.06
        if ref_speeds == 'REF SPEEDS INCR':
            if flap == '15':
                final_ldr = final_ldr * 1.25
            if flap == '35':
                final_ldr = final_ldr * 1.2
        if wet_dry == 'WET':
            final_ldr = final_ldr * 1.67
        else:
            final_ldr = final_ldr * 1.43
        final_ldr = str(round(final_ldr))
        print(final_ldr, "the final LDR")
        self.ldr_txt(final_ldr)

MainApp().run()
