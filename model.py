import torch
import torch.nn as nn
import torch.optim as optim

input_size = 13
action_size = 4
gamma = 0.9
lr  = 0.0001

path = 'model.pth'

class Model(nn.Module):
    def __init__(self):
        super(Model, self).__init__()
        self.fc1 = nn.Linear(input_size, 32)
        self.fc2 = nn.Linear(32, 32)
        self.fc3 = nn.Linear(32, 32)
        self.fc4 = nn.Linear(32,  action_size)
        
    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = torch.relu(self.fc3(x))
        x = torch.sigmoid(self.fc4(x))               ### torch.sigmoid
        return x


model = Model()


criterior = nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr=lr)


def train_step(state, action, reward, next_state, done):
    state = state.unsqueeze(0)  # Добавляем batch размерность
    next_state = next_state.unsqueeze(0)  # Добавляем batch размерность

    action = torch.tensor([action], dtype=torch.int64)
    reward = torch.tensor([reward], dtype=torch.float32)
    done = torch.tensor([done], dtype=torch.bool)

    Q_values = model(state)
    next_Q_values = model(next_state)
    
    # Индексирование по действию
    Q_value = Q_values.gather(1, action.unsqueeze(1)).squeeze(1)
    
    # Целевое значение
    target_Q = reward + gamma * torch.max(next_Q_values, dim=1)[0].detach()
    target_Q = torch.where(done, reward, target_Q)
    
    # Вычисление ошибки
    loss = criterior(Q_value, target_Q)
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

