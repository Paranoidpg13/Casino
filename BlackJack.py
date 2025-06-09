# import random


# card_categories = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
# cards_list = ['Ace', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King']
# deck = [(card, category) for category in card_categories for card in cards_list]

# def calculate_score(cards):
#     score = 0
#     ace_count = 0

#     for card in cards:
#         if card[0] in ['Jack', 'Queen', 'King']:
#             score += 10
#         elif card[0] == 'Ace':
#             score += 11
#             ace_count += 1
#         else:
#             score += int(card[0])

#     while score > 21 and ace_count:
#         score -= 10
#         ace_count -= 1

#     return score

# random.shuffle(deck)
# player_card = [deck.pop(), deck.pop()]
# dealer_card = [deck.pop(), deck.pop()]

# while True:
#     player_score = calculate_score(player_card)
#     dealer_score = calculate_score(dealer_card)
#     print("Cards Player Has:", player_card)
#     print("Score Of The Player:", player_score)
#     print("\n")
#     choice = input('What do you want? ["play" to request another card, "stop" to stop]: ').lower()
#     if choice == "play":
#         new_card = deck.pop()
#         player_card.append(new_card)
#     elif choice == "stop":
#         break
#     else:
#         print("Invalid choice. Please try again.")
#         continue

#     if player_score > 21:
#         print("Cards Dealer Has:", dealer_card)
#         print("Score Of The Dealer:", dealer_score)
#         print("Cards Player Has:", player_card)
#         print("Score Of The Player:", player_score)
#         print("Dealer wins (Player Loss Because Player Score is exceeding 21)")
#         break

# while dealer_score < 17:
#     new_card = deck.pop()
#     dealer_card.append(new_card)
#     dealer_score = calculate_score(dealer_card)

# print("Cards Dealer Has:", dealer_card)
# print("Score Of The Dealer:", dealer_score)
# print("\n")

# if dealer_score > 21:
#     print("Cards Dealer Has:", dealer_card)
#     print("Score Of The Dealer:", dealer_score)
#     print("Cards Player Has:", player_card)
#     print("Score Of The Player:", player_score)
#     print("Player wins (Dealer Loss Because Dealer Score is exceeding 21)")
# elif player_score > dealer_score:
#     print("Cards Dealer Has:", dealer_card)
#     print("Score Of The Dealer:", dealer_score)
#     print("Cards Player Has:", player_card)
#     print("Score Of The Player:", player_score)
#     print("Player wins (Player Has High Score than Dealer)")
# elif dealer_score > player_score:
#     print("Cards Dealer Has:", dealer_card)
#     print("Score Of The Dealer:", dealer_score)
#     print("Cards Player Has:", player_card)
#     print("Score Of The Player:", player_score)
#     print("Dealer wins (Dealer Has High Score than Player)")
# else:
#     print("Cards Dealer Has:", dealer_card)
#     print("Score Of The Dealer:", dealer_score)
#     print("Cards Player Has:", player_card)
#     print("Score Of The Player:", player_score)
#     print("It's a tie.")

import sys
import random
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt

# Card class
class Card:
    def __init__(self, face, value, suit):
        self.face = face
        self.value = value
        self.suit = suit

# Blackjack GUI class
class BlackjackGame(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Blackjack - PyQt5 GUI")
        self.setGeometry(200, 200, 600, 400)
        
        # Layouts
        self.vbox = QVBoxLayout()
        self.dealer_box = QHBoxLayout()
        self.player_box = QHBoxLayout()
        self.controls = QHBoxLayout()
        
        # Labels for cards
        self.dealer_label = QLabel("Dealer's Cards:")
        self.player_label = QLabel("Player's Cards:")
        self.result_label = QLabel("Game in Progress")
        self.result_label.setAlignment(Qt.AlignCenter)
        self.dealer_score_label = QLabel("Dealer Score: 0")
        self.player_score_label = QLabel("Player Score: 0")

        # Align dealer/player labels and scores
        self.dealer_layout = QHBoxLayout()
        self.dealer_layout.addWidget(self.dealer_label)
        self.dealer_layout.addStretch()
        self.dealer_layout.addWidget(self.dealer_score_label)
        
        self.player_layout = QHBoxLayout()
        self.player_layout.addWidget(self.player_label)
        self.player_layout.addStretch()
        self.player_layout.addWidget(self.player_score_label)
        
        # Buttons
        self.hit_btn = QPushButton("Hit")
        self.stand_btn = QPushButton("Stand")
        self.restart_btn = QPushButton("Restart")
        
        self.hit_btn.clicked.connect(self.hit)
        self.stand_btn.clicked.connect(self.stand)
        self.restart_btn.clicked.connect(self.restart)
        
        # Add widgets to layouts
        self.vbox.addLayout(self.dealer_layout)
        self.vbox.addLayout(self.dealer_box)
        self.vbox.addLayout(self.player_layout)
        self.vbox.addLayout(self.player_box)
        self.vbox.addWidget(self.result_label)
        
        self.controls.addWidget(self.hit_btn)
        self.controls.addWidget(self.stand_btn)
        self.controls.addWidget(self.restart_btn)
        
        self.vbox.addLayout(self.controls)
        
        self.setLayout(self.vbox)
        self.restart()
    
    def init_deck(self):
        suits = ['♠', '♥', '♦', '♣']
        faces = {'A': 11, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 10, 'Q': 10, 'K': 10}
        deck = [Card(face, value, suit) for suit in suits for face, value in faces.items()]
        random.shuffle(deck)
        return deck
    
    def restart(self):
        self.deck = self.init_deck()
        self.player_cards = []
        self.dealer_cards = []
        self.player_score = 0
        self.dealer_score = 0
        self.game_over = False  # Reset game state

        
        # Clear previous hands
        self.clear_layout(self.dealer_box)
        self.clear_layout(self.player_box)
        
        # Deal initial cards
        for _ in range(2):
            self.player_cards.append(self.deal_card())
            self.dealer_cards.append(self.deal_card())
        
        self.update_display()
        self.hit_btn.setDisabled(False)
        self.stand_btn.setDisabled(False)
        self.result_label.setText("Game in Progress")
    
    def deal_card(self):
        return self.deck.pop()
    
    def calculate_score(self, cards):
        score = sum(card.value for card in cards)
        aces = sum(1 for card in cards if card.face == 'A')
        while score > 21 and aces:
            score -= 10
            aces -= 1
        return score

    def update_display(self):
        self.clear_layout(self.dealer_box)
        self.clear_layout(self.player_box)
        
        for i, card in enumerate(self.dealer_cards):
            color = "red" if card.suit in ['♥', '♦'] else "black"
            if i == 0 and not self.game_over:
                color = "blue"  # Hide the dealer's first card with blue color
                label_text = "🂠"
            else:
                label_text = f"{card.face}{card.suit}"
            
            label = QLabel(label_text)
            label.setFont(QFont("Arial", 16, QFont.Bold))
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet(f"border: 2px solid black; padding: 10px; background: white; color: {color}; min-width: 60px; min-height: 100px;")
            self.dealer_box.addWidget(label)
        
        for card in self.player_cards:
            color = "red" if card.suit in ['♥', '♦'] else "black"
            label = QLabel(f"{card.face}{card.suit}")
            label.setFont(QFont("Arial", 16, QFont.Bold))
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet(f"border: 2px solid black; padding: 10px; background: white; color: {color}; min-width: 60px; min-height: 100px;")
            self.player_box.addWidget(label)
        
        self.player_score = self.calculate_score(self.player_cards)
        self.dealer_score = self.calculate_score(self.dealer_cards)

        self.player_score_label.setText(f"Player Score: {self.player_score}")
        self.dealer_score_label.setText(f"Dealer Score: {self.dealer_score if self.game_over else '?'}")

        if self.player_score > 21:
            self.result_label.setText("Player Busts! Dealer Wins!")
            self.hit_btn.setDisabled(True)
            self.stand_btn.setDisabled(True)
            self.game_over = True

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def hit(self):
        if not self.game_over:
            self.player_cards.append(self.deal_card())
            self.player_score = self.calculate_score(self.player_cards)
            self.update_display()
            
            if self.player_score > 21:
                self.result_label.setText("Player Busts! Dealer Wins!")
                self.hit_btn.setDisabled(True)
                self.stand_btn.setDisabled(True)
                self.game_over = True
                self.update_display()

    def stand(self):
        self.hit_btn.setDisabled(True)
        self.stand_btn.setDisabled(True)
        
        while self.dealer_score < 17:
            self.dealer_cards.append(self.deal_card())
            self.dealer_score = self.calculate_score(self.dealer_cards)
        
        self.game_over = True
        self.update_display()
        
        if self.dealer_score > 21:
            self.result_label.setText("Dealer Busts! Player Wins!")
        elif self.dealer_score > self.player_score:
            self.result_label.setText("Dealer Wins!")
        elif self.dealer_score < self.player_score:
            self.result_label.setText("Player Wins!")
        else:
            self.result_label.setText("It's a Tie!")
        QApplication.processEvents()
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    game = BlackjackGame()
    game.show()
    sys.exit(app.exec_())