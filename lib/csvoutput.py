
import io
import csv


def createMessage(strage, values):
    output = io.StringIO(newline='')
    writer = csv.writer(output, dialect='excel', lineterminator='\n')

    for value in values:
        writer.writerow(value)

    return output.getvalue()


def createMessageByArrayOfDict(values, showtags=None, headers=None):
    output = io.StringIO(newline='')
    writer = csv.writer(output, dialect='excel', lineterminator='\n')
    if headers:
        writer.writerow(headers)
    for v in values:
        writer.writerow([ v[k] for k in showtags ])
    return output.getvalue()
