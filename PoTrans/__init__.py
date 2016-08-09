import polib
import io
from yandex_translate import YandexTranslate, YandexTranslateException


class Translator:
    """
    Класс для перевода po-файлов
    """
    def __init__(self, yandex_key, src_lang=None, dest_lang=None, src_po_file=None):
        """
        Конструктор
        :param yandex_key: ключ для доступа к API яндекс-переводчика
        :param src_lang: исходный язык
        :param dest_lang: язык назначения
        :param src_po_file: исходный po-файл
        :return:
        """
        self.yandex_key = yandex_key
        self.src_lang = src_lang
        self.dest_lang = dest_lang
        self.yandex_translate = YandexTranslate(self.yandex_key)
        if src_po_file is not None:
            self.open_po_fle(src_po_file)

    def open_po_fle(self, po_filename):
        """
        Открыть po-файл
        :param po_filename:
        :return:
        """
        if isinstance(po_filename, io.TextIOWrapper):
            po_filename = po_filename.name
        self.po = polib.pofile(po_filename)

    def _translate_str(self, text, src_lang, dest_lang, return_src_if_empty_result=True, need_print=False):
        """
        Перевести текстовую строку (приватный метод)
        :param text: текст, который нужно перевести
        :param src_lang: исходный язык
        :param dest_lang: конечный язык
        :param return_src_if_empty_result: вернуть исходную строку, если перевод не найден?
        :param need_print: Выводить на экран информацию о результате перевода (для отладки)
        :return: переведённая строка (или исходная, если перевод не найден, и return_src_if_empty_result==True)
        """
        tr = self.yandex_translate.translate(text, "{}-{}".format(self.src_lang, self.dest_lang))
        if tr['code'] == 200 and len(tr['text']) and tr['text'][0]:
            tr_text = tr['text'][0]
        else:
            tr_text = ""
        if need_print:
            print(text + " => " + tr_text)
        if not tr_text and return_src_if_empty_result:
            tr_text = text
        return tr_text

    def go_translate(self, src_lang=None, dest_lang=None, debug=False, usemsgid=False, **kwargs):
        """
        Запустить перевод po-файла
        :param src_lang: исходный язык
        :param dest_lang: конечный язык
        :param break_on: номер строки, на которой нужно остановить процесс, используется для отладки
        :return:
        """
        break_on = kwargs.get("break_on", False)
        if src_lang is None:
            src_lang = self.src_lang
        if dest_lang is None:
            dest_lang = self.dest_lang
        count = len(self.po)
        pos = 0
        prev_percent = -1
        for item in self.po:
            if break_on and break_on == pos:
                break
            pos += 1
            translated = False
            if item.msgstr:
                item.msgstr = self._translate_str(item.msgstr, src_lang, dest_lang, True, debug)
                translated = True
            if item.msgstr_plural:
                for num in item.msgstr_plural:
                    item.msgstr_plural[num] = self._translate_str(item.msgstr_plural[num], True, debug)
                    translated = True
            if not translated and usemsgid:
                if item.msgid:
                    item.msgstr = self._translate_str(item.msgid, src_lang, dest_lang, True, debug)
                    translated = True
                if item.msgid_plural:
                    for num in item.msgid_plural:
                        item.msgstr_plural[num] = self._translate_str(item.msgid_plural[num], True, debug)
                        translated = True
            percent = int(pos * 100 / count)
            if percent != prev_percent:
                prev_percent = percent
                print("### Progress: " + str(percent) + "% ###")

    def save_po_file(self, dest_po_file=None):
        """
        Сохранить результирующий po-файл
        :param dest_po_file: Имя файла
        :return:
        """
        if dest_po_file is None:
            dest_po_file = self.dest_po_file
        self.po.save(dest_po_file)

    def save_mo_file(self, dest_mo_file=None):
        """
        Сохранить mo-файл
        :param dest_mo_file: имя файла
        :return:
        """
        if dest_mo_file is None:
            dest_mo_file = self.dest_mo_file
        self.po.save_as_mofile(dest_mo_file)

