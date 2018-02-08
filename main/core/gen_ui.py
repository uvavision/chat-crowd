from .. import APP_TEMPLATE, LST_META
import os


tmpl_fn = os.join(APP_TEMPLATE, 'chat_template.html')


def gen_searchq():
    ''' price_low: $('#price_low').val(), '''
    lst = []
    for ele in LST_META[0]:
        k = ele.keys()[0]
        lst.append("{}: $('#{}}').val()".format(k))
    return 'entity_value', ', '.join(lst)


def fill_template(in_html):
    content = open(in_html, 'rb').read()
    pattern = ur"\{\{(.+?)\}\}"
    lst_placeholder = []
    for m in re.finditer(pattern, content):
        place_holder = content[m.start(0):m.end(0)]
        print(place_holder)
        lst_placeholder.append(place_holder)
    for place_holder in lst_placeholder:
        html_fn = 'section_{}_{}.html'.format(place_holder[2:-2], role)
        content = content.replace(place_holder, '')


if __name__ == '__main__':
    print(gen_searchq())
