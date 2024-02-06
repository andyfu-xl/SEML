import os
import sys
_ = [sys.path.insert(1, os.path.join(root, d)) for root, dirs, _ in os.walk(os.getcwd()) for d in dirs]

from modules.communicator.communicator import Communicator
from modules.dataparser.dataparser import DataParser
from modules.database import Database
from modules.preprocessor import Preprocessor
# from modules.model import Model

def main():
    communicator = Communicator("localhost", 8440)
    dataparser = DataParser()
    database = Database()
    preprocessor = Preprocessor(database)
    # model = Model()
    
    while True:
        # Receive message
        message = communicator.receive()
        if message == None:
            break

        # Pass the message to data parser
        parsed_message = dataparser.parse_message(message)

        # Process message
        preprocessed_message = preprocessor.preprocess(parsed_message)

        # Perform inference
        # TODO
        # if preprocessed_message is not None:
            # has_aki, mrn = model.predict(preprocessed_message)

        # Page (if necessary)
        # TODO
        # if has_aki:
        #     communicator.page(mrn)

        # Acknowledge message
        communicator.acknowledge()
        # time.sleep(1)

if __name__ == "__main__":
    main()
