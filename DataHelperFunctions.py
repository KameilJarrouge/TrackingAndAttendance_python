def givenSubjectClean(givenSubject):
    return {
        "id": givenSubject["id"],
        "attendance_pre": givenSubject["attendance_pre"],
        "attendance_post": givenSubject["attendance_post"],
        "attendance_present": givenSubject["attendance_present"],
        'attendance_extend': givenSubject['attendance_extend'],
        "time": givenSubject["time"],
        "students": [{"std_id": stdAtt['taken_subject']['student']['id'], 'attId':stdAtt['id'], 'takenSubjectId': stdAtt['taken_subject']['id'], "images":[img['url'] for img in stdAtt['taken_subject']['student']['images']]} for stdAtt in givenSubject["std_attendances"]],
        "cam_url": givenSubject['cam']['cam_url'],
        "profAttId": givenSubject['prof_attendances']["id"],
        "profImageUrl": givenSubject['professor']['images'][0]['url'],
        'restart_start_time': givenSubject['restart_start_time'],
        'restart_duration': givenSubject['restart_duration'],
    }


def camClean(cam):
    return {
        "id": cam['id'],
        "cam_url": cam['cam_url'],
        'schedule': [{"start": schedule['start'], "end":schedule['end']} for schedule in cam['schedule']]
    }


def personClean(person):
    return {
        "id": person["id"],
        'name': person['name'],
        # 'track': person['track'],
        # 'on_blacklist': person['on_blacklist'],
        'images': [{'url': img['url']} for img in person["images"]]
    }
