import os
from django.shortcuts import render
from django.core.files.storage import default_storage
from django.conf import settings
from .models import ECGClassification

from PIL import Image



from .utils.ECGModel import *


num_classes = 4

model = ECGClassifier(num_classes)
MODEL_PATH = os.path.join(settings.BASE_DIR, 'ecg/utils/ecg_classifier.pth')
model.load_state_dict(torch.load(MODEL_PATH, map_location=torch.device('cpu'), weights_only=True))
model.eval()

# Transform for input image
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])

def ecg_questions_fa(request):
    return render(request, 'ecg_fa.html', context={})

def ecg_analyse_fa(request):
    if request.method == 'POST' and request.FILES['image_input']:
        # Save uploaded image
        uploaded_file = request.FILES['image_input']
        code = request.POST.get('code')

        file_path = default_storage.save(f'images/ecg_classification/{uploaded_file.name}', uploaded_file)

        # Load and preprocess the image
        image_path = os.path.join(settings.MEDIA_ROOT, file_path)
        image = Image.open(image_path).convert('RGB')
        input_tensor = transform(image).unsqueeze(0)

        # Run prediction
        with torch.no_grad():
            output = model(input_tensor)
            prediction_value = torch.argmax(output, dim=1).item()

        # Return the uploaded image and prediction result
        prediction_classes = ['Myocardial Infarction',
                                'History of MI',
                                'Abnormal Heartbeat',
                                'Normal ECG']

        prediction_classes_desc = ['A serious condition where blood flow to the heart is blocked, potentially causing permanent heart damage. Early detection through ECG analysis is critical for timely treatment.'
        ,'Identifying patterns in ECG that indicate a past heart attack, helping healthcare providers understand your heart’s condition and tailor ongoing care.'
        ,'Detect irregular heart rhythms that may indicate conditions such as atrial fibrillation or ventricular tachycardia. Accurate diagnosis supports effective management and treatment.'
        ,'Confirmation of a healthy and regular heart rhythm, providing peace of mind or a baseline for ongoing monitoring.']

        prediction_class = prediction_classes[prediction_value]
        prediction_class_desc = prediction_classes_desc[prediction_value]
        ecg_Classification = ECGClassification.objects.create(userid=request.user
                                                                  , code=code
                                                                  , image_input=uploaded_file
                                                                  , prediction_value=prediction_value
                                                                  , prediction_class=prediction_class
                                                                  )
        print(prediction_class)
        return render(request, 'ecg_fa.html', {
            'image_url': f'{settings.MEDIA_URL}{file_path}',
            'prediction_value': prediction_value,
            'prediction_class': prediction_class,
            'prediction_class_desc': prediction_class_desc
        })

    return render(request, 'ecg_fa.html', context={})
