import json
import math
import re
from kivy.clock import Clock
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

    def restore_original_text(self):
        self.root.ids['calc_screen'].ids['_rwy'].text = "[color=#FF3D16]RUNWAY[/color]"
        self.root.ids['calc_screen'].ids['_ldg_wt'].text = "[color=#FF3D16]WEIGHT[/color]"
        self.root.ids['calc_screen'].ids['flap'].text = "[color=#FF3D16]FLAP[/color]"
        self.root.ids['calc_screen'].ids['_wind'].text = "[color=#E5E542]WIND[/color]"
        self.root.ids['calc_screen'].ids['_vapp_add'].text = "[color=#FF3D16]VAPP[/color]"
        self.root.ids['calc_screen'].ids['reduced_np'].text = "[color=#FF3D16]REDUCED/1020RPM[/color]"
        self.root.ids['calc_screen'].ids['ref_speeds'].text = "[color=#FF3D16]REF SPEEDS[/color]"
        self.root.ids['calc_screen'].ids['wet_dry'].text = "[color=#FF3D16]WET OR DRY[/color]"
        self.root.ids['calc_screen'].ids['lda_txt'].text = ""
        self.root.ids['calc_screen'].ids['ldr_txt'].text = ""
        self.root.ids['home_screen'].ids['error_text'].text = ""
        self.root.ids['calc_screen'].ids['ldg_wt'].text = ""
        self.root.ids['calc_screen'].ids['wind'].text = ""
        self.root.ids['calc_screen'].ids['vapp_add'].text = ""
        self.root.ids['calc_screen'].ids['temp'].text = ""
        wat_limit_info = self.root.ids['calc_screen'].ids['wat_limit_info']
        wat_limit_result = self.root.ids['calc_screen'].ids['wat_limit_result']
        wat_limit_info.text = "For WAT calculation, please enter"
        wat_limit_result.text = "airport temp and bleed switch position"
        wat_limit_info.opacity = 0.5
        wat_limit_result.opacity = 0.5


    def enable_button(self):
        runway_ = self.root.ids['calc_screen'].ids['runway_'].text
        ldg_wt_ = self.root.ids['calc_screen'].ids['ldg_wt_'].text
        flap_ = self.root.ids['calc_screen'].ids['flap_'].text
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
        if not vapp_add.text.isdigit():
            self.root.ids['calc_screen'].ids['_vapp_add'].text = "[color=#FF3D16]VAPP[/color]"
        else:
            if vapp_add.text == '0':
                self.root.ids['calc_screen'].ids['_vapp_add'].text = "[b][color=#3E9933]VAPP = VREF[/color][/b]"
            else:
                self.root.ids['calc_screen'].ids[
                    '_vapp_add'].text = "[b][color=#3E9933]VREF + " + vapp_add.text + '[/color][/b]'

    def ldg_wt_txt(self):
        ldg_wt = self.root.ids['calc_screen'].ids['ldg_wt']
        if not ldg_wt.text.isdigit():
            self.root.ids['calc_screen'].ids['_ldg_wt'].text = "[color=#FF3D16]WEIGHT[/color]"
        else:
            self.root.ids['calc_screen'].ids['_ldg_wt'].text = '[b][color=#3E9933]' + ldg_wt.text + " KG[/color][/b]"

    def head_tail(self, wind_comp):
        self.wind_comp = wind_comp

    def wind_component(self, component):
        wind_ = self.root.ids['calc_screen'].ids['wind_']
        _wind = self.root.ids['calc_screen'].ids['_wind']
        try:
            wind_.text = component + self.wind_comp
            _wind.text = '[b][color=#3E9933]' + component + self.wind_comp + "[/color][/b]"
        except:
            pass

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
            go_button = self.root.ids['calc_screen'].ids['go_button']
            go_button.disabled = True
            colour = 'FF3D16'  # red
            self.op = 0
            self.flash = Clock.schedule_interval(self.flashing_ldr, 0.2)
            Clock.schedule_once(self.cancel_flash, 1.2)
        else:
            colour = '3E9933'  # green
        self.root.ids['calc_screen'].ids['ldr_txt'].text = f"[b][u][color=#{colour}]LDR IS " + ldr + "m[/color][/u][/b]"

    def flashing_ldr(self, *args):
        self.root.ids['calc_screen'].ids['ldr_txt'].opacity = self.op
        if self.op == 1:
            self.op -= 1
        else:
            self.op += 1

    def cancel_flash(self, *args):
        self.root.ids['calc_screen'].ids['ldr_txt'].opacity = 1
        self.flash.cancel()
        go_button = self.root.ids['calc_screen'].ids['go_button']
        go_button.disabled = False

    def change_screen(self, screen_name):
        # get the screen manager from the main.kv file
        screen_manager = self.root.ids['screen_manager']
        screen_manager.current = screen_name

    def runway_buttons(self, airport):
        with open('airport_data.json') as ap_data:
            ap = json.load(ap_data)
        try:
            airport_data = ap[airport]
        except:
            self.root.ids['home_screen'].ids['error_text'].text = "[b][color=#FF3D16]UNKNOWN LOCATION[/color][/b]"
            return
        f = 0
        for runway in airport_data:
            f += 1
            rwy_ = "rwy" + str(f)
            rwy_num = self.root.ids['calc_screen'].ids[rwy_]
            self.root.ids['calc_screen'].add_widget(rwy_num)
            self.root.ids['calc_screen'].ids[rwy_].children[0].text = str(runway)
        self.change_screen("calc_screen")

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
        temp = self.root.ids['calc_screen'].ids['temp_'].text
        bleed = self.root.ids['calc_screen'].ids['bleed_'].text
        self.get_lda_and_elev(airport, runway, weight, flap, wind_comp, vapp_add, reduced_np, ref_speeds, wet_dry, temp,
                              bleed)

    def get_lda_and_elev(self, airport, runway, weight, flap, wind_comp, vapp_add, reduced_np, ref_speeds, wet_dry,
                         temp, bleed):
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
        if not weight.isdigit():
            self.root.ids['calc_screen'].ids['ldr_txt'].text = "[b][color=#FF3D16]INCORRECT WEIGHT DATA[/color][/b]"
            return
        if int(weight) < 21500:
            self.root.ids['calc_screen'].ids['ldr_txt'].text = "[b][color=#FF3D16]WEIGHT TOO LOW[/color][/b]"
            return
        if int(weight) > 29000:
            self.root.ids['calc_screen'].ids['ldr_txt'].text = "[b][color=#FF3D16]WEIGHT TOO HIGH[/color][/b]"
            return
        try:
            weight = str(float(re.search(r'\d*', weight).group()) / 1000)
        except:
            self.root.ids['calc_screen'].ids['ldr_txt'].text = "[b][color=#FF3D16]INCORRECT INPUT[/color][/b]"
            return
        wt_up = str(math.ceil(float(weight)))
        wt_down = str(math.floor(float(weight)))
        with open('airport_data.json') as ap_data:
            lda_elev = json.load(ap_data)
        rwy_data = lda_elev[airport][runway]
        LDA = rwy_data['Length']
        elev = rwy_data['Elev']
        elev = int(elev) / 1000
        self.get_final_uld(elev, flap, wt_up, wt_down, weight, upper_wind_comp, lower_wind_comp, wind_digits, vapp_add,
                           reduced_np, ref_speeds, wet_dry)
        self.get_wat_limit(flap, elev, temp, reduced_np, bleed, weight)

    def get_wat_limit(self, flap, elev, temp, reduced_np, bleed, weight):
        weight = int(float(weight) * 1000)
        if temp == "" or bleed == "":
            return
        elev = elev * 2
        if reduced_np == "REDUCED NP":
            rpm = "850"
        else:
            rpm = "1020"
        if bleed == "BLEED ON":
            temp = str(int(temp) + 11)
        if flap == "35":
            ga_flap = "15"
        else:
            ga_flap = "10"

        with open(f'wat_f{ga_flap}.json') as r:
            wat = json.load(r)
        elev_up = math.ceil(elev)
        elev_down = math.floor(elev)
        temp_up = str(math.ceil(int(temp) / 2) * 2)
        temp_down = str(math.floor(int(temp) / 2) * 2)
        # interpolating with the upper temp of the two elevation figures
        try:
            temp_up_up_data = wat[rpm][temp_up][elev_up]
        except:
            self.root.ids['calc_screen'].ids['wat_limit_info'].text = "[b][color=#FF3D16]TEMP TOO HIGH[/color][/b]"
            self.root.ids['calc_screen'].ids['wat_limit_result'].text = "[b][color=#FF3D16]SWITCH BLEED OFF[/color][/b]"
            return
        temp_up_dwn_data = wat[rpm][temp_up][elev_down]
        temp_up_wt = round(temp_up_dwn_data + ((temp_up_up_data - temp_up_dwn_data) * (elev - elev_down)))
        # interpolating with the lower temp of the two elevation figures
        temp_dwn_up_data = wat[rpm][temp_down][elev_up]
        temp_dwn_dwn_data = wat[rpm][temp_down][elev_down]
        temp_dwn_wt = round(temp_dwn_dwn_data + ((temp_dwn_up_data - temp_dwn_dwn_data) * (elev - elev_down)))

        wat_limit = int((temp_up_wt + temp_dwn_wt) / 2)
        wat_limit_info = self.root.ids['calc_screen'].ids['wat_limit_info']
        wat_limit_result = self.root.ids['calc_screen'].ids['wat_limit_result']
        wat_limit_info.text = "[b][color=#8ABDE1]" + str(int(elev * 500)) + "' Elevation " + bleed + " Landing at " + temp + "°C " + "[/color][/b]"
        if wat_limit < weight:
            colour = 'FF3D16'  # red
            self.op_wat = 0
            self.flash_wat = Clock.schedule_interval(self.flashing_wat, 0.2)
            Clock.schedule_once(self.cancel_flash_wat, 1.2)
        else:
            colour = '3E9933'  # green
        wat_limit_result.text = f"[b][color=#{colour}]Max WAT Limit is " + str(wat_limit) + "kg[/color][/b]"
        wat_limit_info.opacity = 1
        wat_limit_result.opacity = 1


    def flashing_wat(self, *args):
        self.root.ids['calc_screen'].ids['wat_limit_result'].opacity = self.op_wat
        if self.op_wat == 1:
            self.op_wat -= 1
        else:
            self.op_wat += 1

    def cancel_flash_wat(self, *args):
        self.root.ids['calc_screen'].ids['wat_limit_result'].opacity = 1
        self.flash_wat.cancel()


    def get_final_uld(self, elev, flap, wt_up, wt_down, weight, upper_wind_comp, lower_wind_comp, wind_digits, vapp_add,
                      reduced_np, ref_speeds, wet_dry):
        with open('ulds.json') as ulds:
            uld_ = json.load(ulds)
        up = math.ceil(elev)
        down = math.floor(elev)
        # interpolating with the upper weight of the two elevation figures
        try:
            wt_up_up_data = uld_[flap][wt_up][up]
        except:
            self.root.ids['calc_screen'].ids['ldr_txt'].text = "[b][color=#FF3D16]INCORRECT INPUT[/color][/b]"
            return
        wt_up_dwn_data = uld_[flap][wt_up][down]
        uld_up_wt = round(wt_up_dwn_data + ((wt_up_up_data - wt_up_dwn_data) * (elev - down)))
        # interpolating with the lower weight of the two elevation figures
        wt_dwn_up_data = uld_[flap][wt_down][up]
        wt_dwn_dwn_data = uld_[flap][wt_down][down]
        uld_dwn_wt = round(wt_dwn_dwn_data + ((wt_dwn_up_data - wt_dwn_dwn_data) * (elev - down)))
        # interpolating for weight between the two elevation interpolated figures
        final_uld = round(uld_dwn_wt + (uld_up_wt - uld_dwn_wt) * (float(weight) - int(wt_down)))
        self.get_wind_correction(flap, final_uld, upper_wind_comp, lower_wind_comp, wind_digits, vapp_add, reduced_np,
                                 ref_speeds, wet_dry)

    def get_wind_correction(self, flap, final_uld, upper_wind_comp, lower_wind_comp, wind_digits, vapp_add, reduced_np,
                            ref_speeds, wet_dry):
        with open('winds.json') as winds:
            ap = json.load(winds)
        if flap == "35" or flap == "15":
            uld_index = (final_uld - 700) / 25
        else:
            uld_index = ((final_uld - 700) / 25) - 1
        up_2 = math.ceil(uld_index)
        down_2 = math.floor(uld_index)
        # interpolating with the upper wind index of the two uld figures
        try:
            wind_up_up_data = ap[flap][upper_wind_comp][up_2]
        except:
            self.root.ids['calc_screen'].ids['ldr_txt'].text = "[b][color=#FF3D16]WIND COMP TOO HIGH[/color][/b]"
            return
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
        self.get_vapp_additive(vapp_add, final_wind_correct, reduced_np, ref_speeds, flap, wet_dry)

    def get_vapp_additive(self, vapp_add, final_wind_correct, reduced_np, ref_speeds, flap, wet_dry):
        vapp_percent_add = 0
        try:
            for kt in range(int(vapp_add)):
                vapp_percent_add += 0.02
        except:
            self.root.ids['calc_screen'].ids['ldr_txt'].text = "[b][color=#FF3D16]INCORRECT INPUT[/color][/b]"
            return
        final_ldr = final_wind_correct * (1 + vapp_percent_add)
        if reduced_np == 'REDUCED NP':
            final_ldr = final_ldr * 1.06
        if ref_speeds == 'REF SPEEDS INCR':
            if flap == '15' or flap == '10':
                final_ldr = final_ldr * 1.25
            if flap == '35':
                final_ldr = final_ldr * 1.2
        if wet_dry == 'WET':
            final_ldr = final_ldr * 1.67
        else:
            final_ldr = final_ldr * 1.43
        final_ldr = str(round(final_ldr))
        self.ldr_txt(final_ldr)


MainApp().run()
