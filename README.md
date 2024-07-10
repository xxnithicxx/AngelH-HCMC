## Introduction
HEINEKEN Vietnam, the leading beer producer in Vietnam, aims to revolutionize the brand experience for consumers. From local retail stores to favorite hangout spots with friends, you can easily spot the brand's promotional materials (banners, posters, LED signs, etc.). These all contribute to creating an engaging and unforgettable experience for customers. However, inspecting and evaluating these layouts through images is time-consuming and costly for the company.

**Your Task:**

Imagine you are a member of HEINEKEN Vietnam's Digital & Technology (D&T) team. Develop an image analysis tool that can automatically detect the following elements:

1. Brand logos: Detect logos of Heineken, Tiger, Bia Viet, Larue, Bivina, Edelweiss, and Strongbow.
2. Products: Identify beer crates and bottles.
3. Consumers: Evaluate the number, activities, and emotions of customers.
4. Promotional materials: Identify posters, banners, and brand advertisements.
5. Image context: Analyze the location—restaurant, bar, grocery store, supermarket, etc.

**Choose one or more business problems to solve. The more issues you address, the higher your chances of winning!**

- **Business Problem 1: Count the number of beer drinkers**
    
    We want to know how many people are drinking HEINEKEN Vietnam beer at the restaurant. Can you identify the number of people drinking HEINEKEN from the images?
    
    - Count the number of people in the images.
    - Identify the number of people drinking HEINEKEN beer.
    
- **Business Problem 2: Detect promotional materials**
    
    We use various promotional materials such as ice buckets, standees, umbrellas, and shelves at events and display points. Can you detect materials with the brand's logo to confirm their presence at the restaurant?
    
    - Find and list materials with the Heineken logo.
    - Precisely identify each type of material (e.g., ice bucket, bottle, can, refrigerator, signboard, poster, display counter, display table, umbrella).
    
- **Business Problem 3: Evaluate event success**
    
    We want to assess the success of events at the restaurant. Can you help detect the number of customers attending and their moods while drinking beer?
    
    - Count the number of people in the images.
    - Analyze the mood and atmosphere of the images (detect emotions).
    
- **Business Problem 4: Monitor marketing staff**
    
    We need to ensure that at least two marketing staff members are deployed at each location. Can you help confirm their presence?
    
    - Identify marketing staff in the images.
    - Confirm whether there are at least two marketing staff members at each restaurant location.
    
- **Business Problem 5: Evaluate in-store presence**
    
    Can you assess the quality of HEINEKEN's presence at grocery/specialty stores? The store must have at least one advertisement with our logo, one refrigerator with our logo, and at least ten crates of Heineken beer.
    
    Ensure HEINEKEN’s display ideas are correctly implemented at grocery/specialty stores.
    
    - 1 advertisement
    - 1 standee
    - 10 beer crates

👀 To increase your chances of winning, consider the following additional tasks:

- Identify context: Determine the context of the image: whether the restaurant is serving, a supermarket, or a store.
- Identify competitor logos: Detect and identify logos of competitors and other brands in the images.

The toolkit is ready for you:

- [7 Brand Recognition Kits](https://drive.google.com/drive/folders/1gDKDKGUljtxZomBdKxn5dWMBDExVmPMa): Logos along with promotional materials and brand image marketing materials at the point of sale (ice buckets, bottles, cans, refrigerators, signs, posters, display counters, display tables, umbrellas).
- [1000+ Sample Images](https://drive.google.com/drive/folders/1H_eVvr-F0kAY2hiVFuOc7xeoBAiSde3f): Train your tool with the available images.
- [Detailed List of Image Labels, Complete Folder of Logos, and Vector Items](https://drive.google.com/drive/folders/1gDKDKGUljtxZomBdKxn5dWMBDExVmPMa?usp=sharing)
- [50+ Additional Images](https://drive.google.com/drive/folders/1Di_cyaMxMeGwJIBh5z-BoTqaUlB1BodX): Directly evaluate your tool on 30/06/2024.

## Method:
1. Label images with classes such as "beer brand," can, bottle, brand, person, promoter, etc.
2. Fine-tune the YOLOv8 model with this custom dataset to obtain the best model weights.
3. Use Hume AI to detect emotions.
4. Build an application to input images and display images with object bounding boxes, emotion bounding boxes, and image context.

## Set-up
1. `pip install -r requirements.txt`
2. `streamlit run .\app.py`