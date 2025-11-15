# Patient Review Dashboard - Task Spec

**Time Remaining:** 3 hours | **Scope:** MVP for Hackathon

## Core Features

### 1. Patient Dashboard (30 min)
- **List View**: Display all patients with:
  - Name, age, gender
  - Review status badge (needs review / reviewed)
  - Last follow-up date
- **Sorting**: Prioritize patients needing review
- **Action**: Click patient → navigate to profile

### 2. Patient Profile Page (45 min)
- **Patient Info**: Display personal details at top
- **Follow-ups Timeline**: List all follow-ups chronologically
  - Date, X-ray images (thumbnail + expandable)
  - ML Labels (auto-generated)
  - Doctor Labels (confirmed/edited)
  - Status indicator (pending review / confirmed)

### 3. Label Review & Confirmation (45 min)
- **Quick Confirm**: Button to accept ML labels as Doctor labels
- **Edit Mode**: Toggle to modify doctor labels
  - Checkbox list of findings
  - Save changes → update database
- **Visual Feedback**: Show differences between ML and Doctor labels

### 4. Upload New Finding (30 min)
- **Upload Button**: Add new follow-up for patient
- **File Upload**: X-ray image upload
- **Auto-Generate**: Trigger ML model inference
- **Display**: Show new follow-up with ML labels immediately

## API Endpoints Needed

```
GET    /api/patients                    # List all patients + review status
GET    /api/patients/:id                # Patient details + all exams/images
POST   /api/patients/:id/exams          # Upload exam + image, run ML, return predictions
PUT    /api/images/:id/labels           # Update doctor labels for an image
```

## Implementation Notes

- **Upload Flow**: POST multipart/form-data (file + exam metadata) → create Exam → create Image with bytes → run ML inference → return with predictions
- **Review Status**: Image is pending review if `reviewed_at` is NULL. Set timestamp when doctor confirms/edits labels.
- **Doctor Labels**: Create `DoctorLabel` records + update `Image.reviewed_at` when doctor clicks confirm/edit button

## UI Components Priority

1. PatientList (table with status badges)
2. PatientProfile (layout with timeline)
3. FollowUpCard (displays images + labels)
4. LabelReview (comparison + edit interface)
5. UploadModal (file upload + processing)

## Out of Scope (Post-Hackathon)

- Advanced filtering/search
- Image annotation tools
- Multi-image comparison
- Audit trail
- Notifications

## Success Criteria

✅ Doctor can see which patients need review  
✅ Doctor can view patient history with images  
✅ Doctor can confirm or edit ML labels  
✅ Doctor can upload new findings and get ML predictions  
