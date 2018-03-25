import json
from tqdm import tqdm
import os
os.environ['domain'] = 'COCO'
from main import coll_anno


if __name__ == '__main__':
    coco = json.load(open('data/coco_annotations/instances_train2014.json', 'r'))
    cocoid2cocourl = {entry['id']: entry['coco_url'] for entry in coco['images']}

    labelid2labelname = {category['id']: category['name'] for category in coco['categories']}
    cocoid2boxanno = {}
    for anno in tqdm(coco['annotations']):
        cocoid = anno['image_id']
        box = anno['bbox']
        if cocoid not in cocoid2boxanno:
            cocoid2boxanno[cocoid] = []
        cocoid2boxanno[cocoid].append({"left": box[0], "top": box[1], "width": box[2], "height": box[3],
                                       "label": labelid2labelname[anno['category_id']]})

    with open('coco_box_anno.json', 'w') as f:
        json.dump(cocoid2boxanno, f)

    caption_annotation = json.load(open('data/coco_annotations/captions_train2014.json', 'r'))
    cocoid2caption = {}
    for anno in caption_annotation['annotations']:
        cocoid = anno['image_id']
        caption = anno['caption']
        if cocoid not in cocoid2caption:
            cocoid2caption[cocoid] = []
        cocoid2caption[cocoid].append(caption)


    for key in tqdm(cocoid2cocourl):
        try:
            r = {"cocoid": key, "url": cocoid2cocourl[key], "boxes": str(cocoid2boxanno[key]), "captions": str(cocoid2caption[key])}
            coll_anno.insert(r)
        except KeyError as e:
            pass




