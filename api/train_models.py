import numpy as np
import joblib
from sklearn.linear_model import LogisticRegression

# Create specialist model for Hospital C (good at detecting Hernia)
print("Training specialist model (Hospital C - Hernia expert)...")
X_c = np.vstack([
    np.tile([0, 0, 1, 0], (90, 1)),  # 90 samples of 'No Finding'
    np.tile([1, 1, 0, 1], (10, 1))   # 10 samples of 'Hernia'
])
y_c = np.array([0] * 90 + [1] * 10)

model_c = LogisticRegression(random_state=42, max_iter=200)
model_c.fit(X_c, y_c)

# Create generalist models for Hospital A and B (bad at detecting Hernia)
print("Training generalist models (Hospital A & B - only seen common cases)...")
# Add a tiny bit of noise to make it trainable, but essentially all "No Finding"
X_ab = np.vstack([
    np.tile([0, 0, 1, 0], (98, 1)),  # 98 samples of 'No Finding'
    np.tile([1, 1, 0, 1], (2, 1))    # 2 samples of 'Hernia' (very rare, so they won't learn it well)
])
y_ab = np.array([0] * 98 + [1] * 2)

model_a = LogisticRegression(random_state=42, max_iter=200)
model_a.fit(X_ab, y_ab)

model_b = LogisticRegression(random_state=43, max_iter=200)
model_b.fit(X_ab, y_ab)

# Save models to disk (this is the "Student Library")
print("Saving Student Model Library...")
joblib.dump(model_a, 'student_a.pkl')
joblib.dump(model_b, 'student_b.pkl')
joblib.dump(model_c, 'student_c.pkl')

print("✅ Student Model Library created successfully!")
print("   - student_a.pkl (Generalist)")
print("   - student_b.pkl (Generalist)")
print("   - student_c.pkl (Specialist - Hernia)")
