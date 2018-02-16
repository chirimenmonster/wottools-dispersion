
import io
import csv


def createMessage(strage, values):    
    output = io.StringIO(newline='')
    writer = csv.writer(output, dialect='excel', lineterminator='\n')

    for value in values:
        writer.writerow(value)

    return output.getvalue()
