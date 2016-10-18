from collections import OrderedDict
from statistics import median


def _individual_calc(error_msgs, style_msgs):
    """
    Analyses the given lists of error and style Message objects error_msgs and
    style_msgs for an individual.

    @param List[Message] error_msgs: all of this individual's code errors
    @param List[Message] style_msgs: all of this individual's style issues
    @rtype: List[Tuple[str, List]]
    """

    # {msg.symbol + "(" + msg.object + ")": count}
    all_msgs = error_msgs + style_msgs

    all_num = list(zip(*_calc_helper(all_msgs)))
    error_num = list(zip(*_calc_helper(error_msgs)))
    style_num = list(zip(*_calc_helper(style_msgs)))

    stats = [('Most Frequent Messages', all_num),
             ('Most Frequent Errors', error_num),
             ('Most Frequent Styles', style_num)]

    return stats


def summary(all_msgs):
    """
    Provides a summary of each individual's errors from all_msgs and provide an
    overall summary of the course's performance (if applicable).
    Called by pyta_statistics.

    @param OrderedDict[str, Tuple[List[Message], List[Message]]] all_msgs:
        the tuple of code and error messages for each student's files
    @rtype: Tuple[OrderedDict[str, List]]]
    """
    num_stu = len(all_msgs)

    # If directory was for student, not course, return empty summary stats list.
    if num_stu == 1:
        student, stats = all_msgs.popitem()
        return OrderedDict([(student, _individual_calc(*stats))]), OrderedDict()

    indiv_stats = OrderedDict()
    code_errors = []
    style_errors = []
    stu_errors = []

    for student in all_msgs:
        # in the form {std1': (<error>, <style>), 'std2': (<error>, <style>), }
        errors, styles = all_msgs[student]
        indiv_stats[student] = _individual_calc(errors, styles)
        stu_errors.append(len(errors) + len(styles))

        # To find Most Frequent Errors (aggregate)
        code_errors.append(errors)
        style_errors.append(styles)

    error_num = _frequent_messages(_message_counter(code_errors))
    style_num = _frequent_messages(_message_counter(style_errors))
    both_num = _frequent_messages(_message_counter(code_errors + style_errors))

    # Calculating the Five Number Summary for all errors (per student)
    stu_errors.sort(reverse=True)

    med = median(stu_errors)

    q3 = stu_errors[round(0.25 * len(stu_errors))]
    q1 = stu_errors[round(0.75 * len(stu_errors))]

    sum_stats = [('Top 5 Frequent Code Errors', error_num),
                 ('Average Code Errors Per Student',
                  round(len(code_errors) / num_stu, 2)),
                 ('Top 5 Frequent Style Errors', style_num),
                 ('Average Style Errors Per Student',
                  round(len(style_errors) / num_stu, 2)),
                 ('Top 5 Frequent Errors of Either Type', both_num),
                 ('Average Errors of Either Type Per Student',
                  round((len(code_errors) + len(style_errors)) / num_stu, 2)),
                 ('Five Number Summary of Errors Per Student',
                  [('Most Errors', stu_errors[0]),
                   ('Upper Quartile (Q3)', q3),
                   ('Median', med),
                   ('Lower Quartile (Q1)', q1),
                   ('Least Errors', stu_errors[-1])])]

    return indiv_stats, sum_stats


def _calc_helper(msgs):
    """Returns frequent messages in numbers and in percentages.

    @param List[Message] msgs: Message objects for all errors found by linters
    @rtype: List[List]
    """
    # get dict of values {id:int, id2:int}
    msgs_dict = _message_counter(msgs)
    # sort into list of tuple, highest on top
    freq_nums = _frequent_messages(msgs_dict)
    total_msgs = len(msgs)
    # divide each value by total and round to two places
    for message in msgs_dict:
        msgs_dict[message] = round((msgs_dict[message]/total_msgs * 100), 2)
    perc_nums = _frequent_messages(msgs_dict)
    return [freq_nums, perc_nums]


def _message_counter(msgs):
    """Returns the number of errors for every type of error in msgs.

    @param List[Message] msgs: any given Message objects for errors
    @rtype: Dict[str, int]
    """

    msgs = msgs.copy()  # prevent aliasing
    msgs_dict = {}

    for msg in msgs:
        key = msg.msg_id + " (" + msg.symbol + ")"
        if key not in msgs_dict:
            msgs_dict[key] = sum(1 for m in msgs if m.msg_id == msg.msg_id)
    return msgs_dict


def _frequent_messages(comp_dict, top=5):
    """
    Sort the errors in comp_dict from the most frequent to least frequent in a
    list.
    Return top couple most frequently occurred errors.

    @type comp_dict: Dict[str, number]
    @type top: int
    @rtype: List[Tuple[str, number]]
    """
    # get key-value pair in a list
    most_frequently = list(comp_dict.items())
    # sort the list according to the value, from larger number to lower number
    most_frequently.sort(key=lambda p: p[1], reverse=True)
    # So the name of the error first and then the number of its occurrence.
    # return the top whatever number
    return most_frequently[0:top]