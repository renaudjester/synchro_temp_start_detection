import os
import urllib.request, json
import pandas as pd


def get_index(list_dict, vid_name):
    """helper to read the json file."""
    index = -1
    for i in range(len(list_dict)):
        if list_dict[i]['name'] == vid_name:
            index = i
    return index


def correct_automatique(url_course, csv_save_path):
    with urllib.request.urlopen(os.path.join(url_course)) as url:
        files = json.loads(url.read().decode())
        auto_csv = [elmt for elmt in files if 'automatique' in elmt['name']]
    if not auto_csv:
        return -1
    df = pd.read_csv(os.path.join(url_course, auto_csv[0]['name']))
    # df.to_csv(os.path.join('../backup/', auto_csv[0]['name']), index=False)
    df['swimmer'] = df['swimmer'] + 1
    df['xd'] = df['x1']
    df['yd'] = df['y1']
    df['x'] = df['x2']
    df['y'] = df['y2']
    df = df.drop(columns=['Unnamed: 0', 'x1', 'y1', 'y2', 'x2'])
    print(auto_csv[0]['name'])
    df.to_csv(os.path.join(csv_save_path, auto_csv[0]['name']), index=False)
    return auto_csv[0]['name']

def correct_manuel(url_course, csv_save_path):
    with urllib.request.urlopen(os.path.join(url_course)) as url:
        files = json.loads(url.read().decode())
        man_csv = [elmt for elmt in files if 'manuel' in elmt['name']]
    print(url_course)
    if not man_csv:
        return -1

    try:
        with urllib.request.urlopen(os.path.join(url_course, url_course.split('/')[-1] + '.json')) as url:
            json_course = json.loads(url.read().decode())
        print(json_course)
    except:
        return -1

    name_of_video = [elmt['name'] for elmt in files if 'from_above' in elmt['name']]
    if not name_of_video:
        return -1

    index_vid = get_index(json_course['videos'], name_of_video)
    fps = json_course['videos'][index_vid]['fps']
    print(fps)
    df = pd.read_csv(os.path.join(url_course, man_csv[0]['name']))
    df.to_csv(os.path.join('../backup/', man_csv[0]['name']), index=False)

def save_to_dataroom(csv_to_send, compet, course, name_on_dataroom):
    os.system('curl -X PUT --user neptune:neptune --data-binary @'
              + "'" + csv_to_send + "' "
              + os.path.join('http://dataroom.liris.cnrs.fr:8080/remote.php/webdav/pipeline-tracking/',
                             compet,  # compet
                             course,  # course
                             name_on_dataroom, # file name on dataroom
                             )
              )


if __name__ == "__main__":
    url_dataroom = "https://dataroom.liris.cnrs.fr/vizvid_json/pipeline-tracking/"
    with urllib.request.urlopen(url_dataroom) as url:
        pipeline_tracking = json.loads(url.read().decode())
        print(pipeline_tracking)

    dir_pipeline_tracking = [elmt for elmt in pipeline_tracking if elmt['type'] == 'directory' and '20' in elmt['name']]
    print(dir_pipeline_tracking)

    # for the analysis made with the automatic model
    for compet in dir_pipeline_tracking:
        with urllib.request.urlopen(os.path.join(url_dataroom, compet['name'])) as url:
            all_course = json.loads(url.read().decode())
            all_course = [elmt for elmt in all_course if elmt['type'] == 'directory' and '20' in elmt['name']]
            for course in all_course:
                course_name = course['name']
                manuel_csv_name = correct_manuel(os.path.join(url_dataroom, compet['name'], course_name), '../test/')
                # if auto_csv_name != -1:
                #     save_to_dataroom(os.path.join('../test/', auto_csv_name), compet['name'], course_name, auto_csv_name)

    ## for the analysis made with the automatic model
    # for compet in dir_pipeline_tracking:
    #     with urllib.request.urlopen(os.path.join(url_dataroom, compet['name'])) as url:
    #         all_course = json.loads(url.read().decode())
    #         all_course = [elmt for elmt in all_course if elmt['type'] == 'directory' and '20' in elmt['name']]
    #         print(all_course)
    #         for course in all_course:
    #             course_name = course['name']
    #             auto_csv_name = correct_automatique(os.path.join(url_dataroom, compet['name'], course_name), '../test/')
    #             if auto_csv_name != -1:
    #                 save_to_dataroom(os.path.join('../test/', auto_csv_name), compet['name'], course_name, auto_csv_name)