# -*- coding: utf-8 -*-
# project: pRodriguezAssistant

class PsLiveRecognizer:
    def __init__(self, resources_dir, lang, parameter_set):
        self.resources_dir = resources_dir
        self.parameter_set = parameter_set
        self.lang = lang
        self.generatePsCmdLine()

    def generatePsCmdLine(self):
        if self.lang == 'en':
            self.cmd_line = '''pocketsphinx_continuous -adcdev plughw:1,0''' \
                        + ' -lm ' + self.resources_dir + self.lang + '/' + self.parameter_set + '.lm' \
                        + ' -dict ' + self.resources_dir + self.lang + '/' + self.parameter_set + '.dic' \
                        + ' -dictcase yes -inmic yes ' \
                        + ' -jsgf ' + self.resources_dir + self.lang + '/' + self.parameter_set + '.jsgf' \
                        + ' -ds 3'
                        #+ ' -logfn /dev/null ' \
        else:
            self.cmd_line = '''pocketsphinx_continuous -adcdev plughw:1,0''' \
                            + ' -hmm ' + self.resources_dir + self.lang + '/lm/zero_ru.cd_semi_4000/' \
                            + ' -dict ' + self.resources_dir + self.lang + '/' + self.parameter_set + '.dic' \
                            + ' -dictcase yes -inmic yes ' \
                            + ' -jsgf ' + self.resources_dir + self.lang + '/' + self.parameter_set + '.jsgf' \
                            + ' -ds 3'
                            #+ ' -logfn /dev/null ' \
