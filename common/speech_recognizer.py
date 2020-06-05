# -*- coding: utf-8 -*-
# project: pRodriguezAssistant

class PsLiveRecognizer:
    def __init__(self, common_res_dir, profile_res_dir, lang, parameter_set):
        self.common_res_dir = common_res_dir
        self.profile_res_dir = profile_res_dir
        self.parameter_set = parameter_set
        self.lang = lang
        self.generatePsCmdLine()

    def generatePsCmdLine(self):
        if self.lang == 'en':
            self.cmd_line = '''pocketsphinx_continuous -adcdev plughw:1,0''' \
                        + ' -hmm ' + self.common_res_dir + self.lang + '/cmusphinx-en-us-ptm-8khz-5.2' \
                        + ' -dict ' + self.profile_res_dir + self.lang + '/' + self.parameter_set + '.dic' \
                        + ' -dictcase yes -inmic yes ' \
                        + ' -jsgf ' + self.profile_res_dir + self.lang + '/' + self.parameter_set + '.jsgf' \
                        + ' -ds 3 -samprate 8000 '
                        #+ ' -logfn /dev/null ' \
        else:
            self.cmd_line = '''pocketsphinx_continuous -adcdev plughw:1,0''' \
                            + ' -hmm ' + self.common_res_dir + self.lang + '/zero_ru.cd_semi_4000/' \
                            + ' -dict ' + self.profile_res_dir + self.lang + '/' + self.parameter_set + '.dic' \
                            + ' -dictcase yes -inmic yes ' \
                            + ' -jsgf ' + self.profile_res_dir + self.lang + '/' + self.parameter_set + '.jsgf' \
                            + ' -ds 3 -samprate 8000 ' \
                            # + ' -logfn /dev/null '
                            # + ' -remove_noise no '

