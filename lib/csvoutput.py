
import io
import csv


def createMessage(strage, values):    
    output = io.StringIO(newline='')
    writer = csv.writer(output, dialect='excel', lineterminator='\n')

    for value in values:
        writer.writerow(value)

    return output.getvalue()


def createMessageByArrayOfDict(values):
    output = io.StringIO(newline='')
    writer = csv.writer(output, dialect='excel', lineterminator='\n')
    ks = values[0].keys()
    writer.writerow(ks)
    for v in values:
        writer.writerow([ v[k] for k in ks ])
    return output.getvalue()
    