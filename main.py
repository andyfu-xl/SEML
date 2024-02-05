import time

from modules.communicator.communicator import Communicator
# from modules.dataparser.dataparser import DataParser
# from modules.preprocessor import Preprocessor
# from modules.model import Model

def main():
    communicator = Communicator("localhost", 8440)
    # dataparser = DataParser()
    # preprocessor = Preprocessor()
    # model = Model()
    
    while True:
        # Receive message
        message = communicator.receive()
        if message == None:
            break
        print(message)

        # Pass the message to data parser
        # TODO
        # parsed_message = dataparser.parse(message)

        # Process message
        # TODO
        # preprocessed_message = preprocessor.preprocess(parsed_message)

        # Perform inference
        # TODO
        # has_aki, mrn = model.predict(preprocessed_message)

        # Page (if necessary)
        # TODO
        # if has_aki:
        #     communicator.page(mrn)

        # Acknowledge message
        communicator.acknowledge()
        time.sleep(1)

if __name__ == "__main__":
    main()
