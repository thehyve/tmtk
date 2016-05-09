feedback_categories = ['errors', 'warnings', 'infos']


def get_feedback_dict():
    feedback_dict = {}
    for feedback_category in feedback_categories:
        feedback_dict[feedback_category] = []
    return feedback_dict


def merge_feedback_dicts(*args):
    feedback_dict = get_feedback_dict()
    for arg in args:
        for feedback_category in feedback_categories:
            if feedback_category in arg:
                feedback_dict[feedback_category] += arg[feedback_category]
            else:
                msg = "Feedback category {} missing.".format(feedback_category)
                raise Exception(msg)
    return feedback_dict
