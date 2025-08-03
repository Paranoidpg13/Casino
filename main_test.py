import tkinter as tk 
from tkinter import *
import random
from PIL import Image, ImageTk
from tkinter import messagebox
from collections import Counter



class IntroPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        tk.Label(self, text="Welcome to the Casino!", font=("Arial", 24)).pack(pady=40)

        tk.Button(self, text="Play Blackjack", font=("Arial", 14),
                  command=controller.bj.show).pack(pady=10)
        tk.Button(self, text="Play Texas Hold 'em", font=("Arial", 14),
                  command=controller.poker.show).pack(pady=10)
        tk.Button(self, text="Play Roulette", font=("Arial", 14),
                  command=controller.roulette.show).pack(pady=10)
    def show(self):
        self.lift()

class MainView(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        buttonframe = tk.Frame(self)
        container = tk.Frame(self)
        buttonframe.pack(side="top", fill="x", expand=False)
        container.pack(side="top", fill="both", expand=True)

        self.bankroll = 1000
        self.bankroll_var = tk.StringVar(value=f"Bankroll: ${self.bankroll}")
        tk.Label(buttonframe, textvariable=self.bankroll_var, font=("Arial", 14)).pack(side="right", padx=20)

        # Create game frames first
        self.bj = BJ(container, self)
        self.poker = Poker(container, self)
        self.roulette = Roulette(container, self)

        # THEN create the intro page
        self.intro = IntroPage(container, self)

        # Place all frames
        for frame in (self.intro, self.bj, self.poker, self.roulette):
            frame.place(x=0, y=0, relwidth=1, relheight=1)

        # Navigation buttons (optional)
        b1 = tk.Button(buttonframe, text="BlackJack", command=self.bj.show)
        b2 = tk.Button(buttonframe, text="Texas Hold 'em", command=self.poker.show)
        b3 = tk.Button(buttonframe, text="Roulette", command=self.roulette.show)
        b1.pack(side="left")
        b2.pack(side="left")
        b3.pack(side="left")

        self.intro.show()  # Show intro page first
    def update_bankroll(self):
        self.bankroll_var.set(f"Bankroll: ${self.bankroll}")


# Add show method to each frame
def add_show_method(cls):
    def show(self):
        self.tkraise()
    cls.show = show
    return cls




@add_show_method
class BJ(tk.Frame):
    def __init__(self, parent, main_view, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.main_view = main_view
        self.configure(bg="green")

        self.deck = []
        self.dealer = []
        self.player = []
        self.dealer_score = []
        self.player_score = []
        self.blackjack_status = {"dealer": "no", "player": "no"}
        self.dealer_spot = 0
        self.player_spot = 0
        self.bet_amount_var = tk.StringVar(value="100")
        tk.Label(self, text="Bet Amount:", bg="green", fg="white").pack()
        tk.Entry(self, textvariable=self.bet_amount_var, width=10).pack(pady=5)

        self.build_ui()
        self.shuffle_deck()
    def show(self):
        self.lift()
    def build_ui(self):
        
        
        # Buttons
        button_frame = tk.Frame(self, bg="green")
        button_frame.pack(pady=20)

        self.shuffle_button = tk.Button(button_frame, text="Shuffle", font=("Helvetica", 14), command=self.shuffle_deck)
        self.shuffle_button.grid(row=0, column=0)

        self.card_button = tk.Button(button_frame, text="Hit Me!", font=("Helvetica", 14), command=self.player_hit)
        self.card_button.grid(row=0, column=1, padx=10)

        self.stand_button = tk.Button(button_frame, text="Stand!", font=("Helvetica", 14), command=self.stand)
        self.stand_button.grid(row=0, column=2)

        self.reset_button = tk.Button(button_frame, text="Reset", font=("Helvetica", 14), command=lambda: self.reset_game(redeal=True))
        self.reset_button.grid(row=0, column=3, padx=10)
        self.reset_button.config(state="disabled")

        # Card frames
        self.my_frame = tk.Frame(self, bg="green")
        self.my_frame.pack(pady=20)

        self.dealer_frame = tk.LabelFrame(self.my_frame, text="Dealer", bd=0)
        self.dealer_frame.pack(padx=20, ipadx=20)

        self.player_frame = tk.LabelFrame(self.my_frame, text="Player", bd=0)
        self.player_frame.pack(ipadx=20, pady=10)

        # Dealer and Player card labels
        self.dealer_labels = [tk.Label(self.dealer_frame) for _ in range(5)]
        for i, label in enumerate(self.dealer_labels):
            label.grid(row=0, column=i, padx=20, pady=20)

        self.player_labels = [tk.Label(self.player_frame) for _ in range(5)]
        for i, label in enumerate(self.player_labels):
            label.grid(row=1, column=i, padx=20, pady=20)

    def resize_card(self, card_path):
        img = Image.open(card_path)
        img = img.resize((150, 218))
        return ImageTk.PhotoImage(img)

    def shuffle_deck(self):
        suits = ["diamonds", "clubs", "hearts", "spades"]
        values = range(2, 15)
        self.deck = [f"{v}_of_{s}" for s in suits for v in values]
        random.shuffle(self.deck)

        bet = self.validate_bet()
        if bet is None:
            return

        if bet > self.main_view.bankroll:
            messagebox.showerror("Error", "Not enough funds!")
            return

        self.current_bet = bet
        self.main_view.bankroll -= bet
        self.main_view.update_bankroll()

        self.reset_game(clear_only=True)

        # Initial deal
        self.dealer_hit()
        self.dealer_hit(hide=True)
        self.player_hit()
        self.player_hit()

    def reset_game(self, clear_only=False, redeal=False):
        self.dealer = []
        self.player = []
        self.dealer_score = []
        self.player_score = []
        self.dealer_spot = 0
        self.player_spot = 0
        self.blackjack_status = {"dealer": "no", "player": "no"}

        for label in self.dealer_labels + self.player_labels:
            label.config(image='')
            label.image = None

        self.card_button.config(state="normal")
        self.stand_button.config(state="normal")
        self.reset_button.config(state="disabled")

        # if not clear_only and len(self.deck) < 10:
        #     messagebox.showinfo("Reshuffling", "Deck is low. Reshuffling new deck.")
        #     self.shuffle_deck()
        if redeal:
            if len(self.deck) < 10:
                messagebox.showinfo("Reshuffling", "Deck is low. Reshuffling new deck")
            else:
                self.dealer_hit()
                self.dealer_hit(hide=True)
                self.player_hit()
                self.player_hit()
    def player_hit(self):
        if self.player_spot >= 5:
            return
        card = self.draw_card(self.player, self.player_score)
        img = self.resize_card(f'cards/{card}.png')
        self.player_labels[self.player_spot].config(image=img)
        self.player_labels[self.player_spot].image = img
        self.player_spot += 1
        self.check_blackjack("player")

    def dealer_hit(self, hide=False):
        if self.dealer_spot >= 5:
            return
        card = self.draw_card(self.dealer, self.dealer_score)

        if hide:
            img = self.resize_card('cards/back.png')
        else:
            img = self.resize_card(f'cards/{card}.png')
        
        self.dealer_labels[self.dealer_spot].config(image=img)
        self.dealer_labels[self.dealer_spot].image = img
        self.dealer_spot += 1

        if not hide:
            self.check_blackjack("dealer")
        
        # card = self.draw_card(self.dealer, self.dealer_score)
        # img = self.resize_card(f'cards/{card}.png')
        # self.dealer_labels[self.dealer_spot].config(image=img)
        # self.dealer_labels[self.dealer_spot].image = img
        # self.dealer_spot += 1
        # self.check_blackjack("dealer")

    def draw_card(self, hand, score_list):
        card = self.deck.pop()
        hand.append(card)
        value = int(card.split("_", 1)[0])
        if value == 14:
            score_list.append(11)
        elif value in [11, 12, 13]:
            score_list.append(10)
        else:
            score_list.append(value)
        return card

    def validate_bet(self):
        try:
            bet = int(self.bet_amount_var.get())
            if bet <= 0:
                messagebox.showerror("Error", "Bet must be positive.")
                return None
            if bet > self.main_view.bankroll:
                messagebox.showerror("Error", "Not enough funds!")
                return None
            return bet
        except ValueError:
            messagebox.showerror("Error", "Enter a valid bet.")
            return None

    def check_blackjack(self, who):
        score_list = self.player_score if who == "player" else self.dealer_score
        total = sum(score_list)

        # Adjust ace(s) if bust
        while total > 21 and 11 in score_list:
            idx = score_list.index(11)
            score_list[idx] = 1
            total = sum(score_list)

        if total == 21:
            self.blackjack_status[who] = "yes"
        elif total > 21:
            self.blackjack_status[who] = "bust"
        else:
            self.blackjack_status[who] = "no"

        self.evaluate_blackjack()

    def evaluate_blackjack(self):
        dealer_status = self.blackjack_status["dealer"]
        player_status = self.blackjack_status["player"]

        # Immediate outcomes
        if player_status == "bust":
            messagebox.showinfo("Player Busts!", "You busted. Dealer wins!")
            self.end_game(player_won=False)
        elif dealer_status == "bust":
            messagebox.showinfo("Dealer Busts!", "Dealer busted. You win!")
            self.end_game(player_won=True)
        elif player_status == "yes" and dealer_status == "yes":
            messagebox.showinfo("Push", "Both got blackjack. It's a tie!")
            self.end_game(player_won=None)
        elif player_status == "yes":
            messagebox.showinfo("Player Wins!", "Blackjack! You win!")
            self.end_game(player_won=True)
        elif dealer_status == "yes":
            messagebox.showinfo("Dealer Wins!", "Blackjack! Dealer wins!")
            self.end_game(player_won=False)

    def stand(self):
        if len(self.dealer) >= 2:    
            second_card = self.dealer[1]
            img = self.resize_card(f'cards/{second_card}.png')
            self.dealer_labels[1].config(image=img)
            self.dealer_labels[1].image = img
        
        
        # Dealer hits until 17 or more
        while sum(self.dealer_score) < 17:
            self.dealer_hit()

        player_total = sum(self.player_score)
        dealer_total = sum(self.dealer_score)

        if dealer_total > 21 or player_total > dealer_total:
            messagebox.showinfo("Player Wins!", f"You win! Player: {player_total}, Dealer: {dealer_total}")
            self.end_game(player_won=True)
        elif dealer_total > player_total:
            messagebox.showinfo("Dealer Wins!", f"Dealer wins! Player: {player_total}, Dealer: {dealer_total}")
            self.end_game(player_won=False)
        else:
            messagebox.showinfo("Push", "It's a tie!")
            self.end_game(player_won=None)

    def end_game(self, player_won=None):
        self.card_button.config(state="disabled")
        self.stand_button.config(state="disabled")
        self.reset_button.config(state="normal")

        # Payout handling
        if player_won is True:
            payout = self.current_bet * 2
            self.main_view.bankroll += payout
            messagebox.showinfo("Payout", f"You won ${payout}!")
        elif player_won is None:  # Tie/push
            self.main_view.bankroll += self.current_bet  # Return bet
            messagebox.showinfo("Push", "Bet returned.")
        else:
            # player lost, bet already deducted
            messagebox.showinfo("Result", "You lost your bet.")

        self.main_view.update_bankroll()

 



@add_show_method
class Poker(tk.Frame):
    def __init__(self, parent, main_view, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.main_view = main_view
        self.configure(bg="darkgreen")

        self.deck = []
        self.community_cards = []
        self.player_hole_cards = []
        self.opponent_hole_cards = []

        self.bankroll = self.main_view.bankroll  # Starting bankroll
        self.pot = 0
        self.bet_amount_var = tk.StringVar(value="100")

        self.build_ui()
        self.shuffle_deck()
    def show(self):
        self.lift()
    def build_ui(self):
        tk.Label(self, text="Poker - Texas Hold'em", bg="darkgreen", fg="white", font=("Helvetica", 16)).pack(pady=10)

        bet_frame = tk.Frame(self, bg="darkgreen")
        bet_frame.pack(pady=10)
        tk.Label(bet_frame, text="Bet Amount:", bg="darkgreen", fg="white").pack(side="left")
        tk.Entry(bet_frame, textvariable=self.bet_amount_var, width=10).pack(side="left", padx=5)

        button_frame = tk.Frame(self, bg="darkgreen")
        button_frame.pack(pady=10)
        self.shuffle_button = tk.Button(button_frame, text="Shuffle/Start", command=self.shuffle_deck)
        self.shuffle_button.pack(side="left", padx=5)

        self.deal_flop_button = tk.Button(button_frame, text="Deal Flop", state="disabled", command=self.deal_flop)
        self.deal_flop_button.pack(side="left", padx=5)

        self.deal_turn_button = tk.Button(button_frame, text="Deal Turn", state="disabled", command=self.deal_turn)
        self.deal_turn_button.pack(side="left", padx=5)

        self.deal_river_button = tk.Button(button_frame, text="Deal River", state="disabled", command=self.deal_river)
        self.deal_river_button.pack(side="left", padx=5)

        self.showdown_button = tk.Button(button_frame, text="Showdown", state="disabled", command=self.showdown)
        self.showdown_button.pack(side="left", padx=5)

        # Card display frames
        self.cards_frame = tk.Frame(self, bg="darkgreen")
        self.cards_frame.pack(pady=10)

        # Opponent hole cards
        opponent_frame = tk.LabelFrame(self.cards_frame, text="Opponent's Cards", bg="darkgreen", fg="white")
        opponent_frame.grid(row=0, column=0, padx=20)
        self.opponent_labels = [tk.Label(opponent_frame, bg="darkgreen") for _ in range(2)]
        for i, lbl in enumerate(self.opponent_labels):
            lbl.grid(row=0, column=i, padx=5)

        # Community cards
        community_frame = tk.LabelFrame(self.cards_frame, text="Community Cards", bg="darkgreen", fg="white")
        community_frame.grid(row=0, column=1, padx=20)
        self.community_labels = [tk.Label(community_frame, bg="darkgreen") for _ in range(5)]
        for i, lbl in enumerate(self.community_labels):
            lbl.grid(row=0, column=i, padx=5)

        # Player hole cards
        player_frame = tk.LabelFrame(self.cards_frame, text="Your Cards", bg="darkgreen", fg="white")
        player_frame.grid(row=0, column=2, padx=20)
        self.player_labels = [tk.Label(player_frame, bg="darkgreen") for _ in range(2)]
        for i, lbl in enumerate(self.player_labels):
            lbl.grid(row=0, column=i, padx=5)

        # Pot and bankroll display
        self.info_label = tk.Label(self, text="", bg="darkgreen", fg="white", font=("Helvetica", 14))
        self.info_label.pack(pady=10)

    def resize_card(self, card_path):
        img = Image.open(card_path)
        img = img.resize((80, 116))
        return ImageTk.PhotoImage(img)

    def shuffle_deck(self):
        suits = ["diamonds", "clubs", "hearts", "spades"]
        values = range(2, 15)  # 11=Jack, 12=Queen, 13=King, 14=Ace
        self.deck = [f"{v}_of_{s}" for s in suits for v in values]
        random.shuffle(self.deck)

        # Clear previous cards
        self.community_cards.clear()
        self.player_hole_cards.clear()
        self.opponent_hole_cards.clear()
        self.pot = 0

        # Clear all card images
        for lbl in self.community_labels + self.player_labels + self.opponent_labels:
            lbl.config(image='')
            lbl.image = None

        # Validate bet
        bet = self.validate_bet()
        if bet is None:
            return

        if bet > self.main_view.bankroll:
            messagebox.showerror("Error", "Not enough bankroll!")
            return

        self.current_bet = bet
        self.main_view.bankroll -= bet
        self.pot += bet * 2  # Both player and opponent ante
        self.main_view.update_bankroll()

        self.info_label.config(text=f"Pot: ${self.pot} | Bankroll: ${self.main_view.bankroll}")

        # Deal hole cards
        self.deal_hole_cards()

        # Enable buttons accordingly
        self.deal_flop_button.config(state="normal")
        self.deal_turn_button.config(state="disabled")
        self.deal_river_button.config(state="disabled")
        self.showdown_button.config(state="disabled")

    def validate_bet(self):
        try:
            bet = int(self.bet_amount_var.get())
            if bet <= 0:
                messagebox.showerror("Error", "Bet must be positive")
                return None
            return bet
        except ValueError:
            messagebox.showerror("Error", "Enter a valid integer bet")
            return None

    def deal_hole_cards(self):
        for i in range(2):
            # Player cards
            card = self.deck.pop()
            self.player_hole_cards.append(card)
            img = self.resize_card(f"cards/{card}.png")
            self.player_labels[i].config(image=img)
            self.player_labels[i].image = img

            # Opponent cards (face down)
            # Show back of card for opponent initially
            back_img = self.resize_card("cards/back.png")
            self.opponent_labels[i].config(image=back_img)
            self.opponent_labels[i].image = back_img

    def deal_flop(self):
        # Burn one card
        self.deck.pop()

        # Deal three community cards
        for i in range(3):
            card = self.deck.pop()
            self.community_cards.append(card)
            img = self.resize_card(f"cards/{card}.png")
            self.community_labels[i].config(image=img)
            self.community_labels[i].image = img

        self.deal_flop_button.config(state="disabled")
        self.deal_turn_button.config(state="normal")

    def deal_turn(self):
        # Burn one card
        self.deck.pop()

        card = self.deck.pop()
        self.community_cards.append(card)
        img = self.resize_card(f"cards/{card}.png")
        self.community_labels[3].config(image=img)
        self.community_labels[3].image = img

        self.deal_turn_button.config(state="disabled")
        self.deal_river_button.config(state="normal")

    def deal_river(self):
        # Burn one card
        self.deck.pop()

        card = self.deck.pop()
        self.community_cards.append(card)
        img = self.resize_card(f"cards/{card}.png")
        self.community_labels[4].config(image=img)
        self.community_labels[4].image = img

        self.deal_river_button.config(state="disabled")
        self.showdown_button.config(state="normal")

    def showdown(self):
    # Reveal opponent cards
        for i, card in enumerate(self.opponent_hole_cards):
            img = self.resize_card(f"cards/{card}.png")
            self.opponent_labels[i].config(image=img)
            self.opponent_labels[i].image = img

        player_rank = self.evaluate_hand(self.player_hole_cards, self.community_cards)
        opponent_rank = self.evaluate_hand(self.opponent_hole_cards, self.community_cards)

        result_msg = (
            f"Your hand: {player_rank[2]}\n"
            f"Opponent hand: {opponent_rank[2]}\n"
        )

        if player_rank[0] > opponent_rank[0]:
            result_msg += "You win!"
            self.main_view.bankroll += self.pot
        elif player_rank[0] < opponent_rank[0]:
            result_msg += "Opponent wins!"
        else:
            # Tie-breaker by kickers
            if player_rank[1] > opponent_rank[1]:
                result_msg += "You win (by kicker)!"
                self.main_view.bankroll += self.pot
            elif player_rank[1] < opponent_rank[1]:
                result_msg += "Opponent wins (by kicker)!"
            else:
                result_msg += "It's a tie!"
                self.main_view.bankroll += self.pot // 2

        self.pot = 0
        self.main_view.update_bankroll()
        self.info_label.config(text=f"Pot: ${self.pot} | Bankroll: ${self.main_view.bankroll}")

        messagebox.showinfo("Showdown Result", result_msg)

        self.shuffle_button.config(state="normal")
        self.deal_flop_button.config(state="disabled")
        self.deal_turn_button.config(state="disabled")
        self.deal_river_button.config(state="disabled")
        self.showdown_button.config(state="disabled")


    # To start with opponent cards (simulate)
    def deal_hole_cards(self):
        self.player_hole_cards.clear()
        self.opponent_hole_cards.clear()

        for i in range(2):
            card_p = self.deck.pop()
            card_o = self.deck.pop()
            self.player_hole_cards.append(card_p)
            self.opponent_hole_cards.append(card_o)

            # Show player cards
            img_p = self.resize_card(f"cards/{card_p}.png")
            self.player_labels[i].config(image=img_p)
            self.player_labels[i].image = img_p

            # Show back of card for opponent initially
            back_img = self.resize_card("cards/back.png")
            self.opponent_labels[i].config(image=back_img)
            self.opponent_labels[i].image = back_img



    def evaluate_hand(self, hole_cards, community_cards):
        all_cards = hole_cards + community_cards
        values = [int(card.split("_")[0]) for card in all_cards]
        suits = [card.split("_of_")[1] for card in all_cards]

        if 14 in values:
            values.append(1)  # Ace as low for straights

        value_counts = Counter(values)
        suit_counts = Counter(suits)

        # Flush detection
        flush_suit = None
        for suit, count in suit_counts.items():
            if count >= 5:
                flush_suit = suit
                break

        flush_cards = []
        if flush_suit:
            flush_cards = sorted(
                [int(card.split("_")[0]) for card in all_cards if card.endswith(flush_suit)],
                reverse=True,
            )
            if 14 in flush_cards:
                flush_cards.append(1)

        def get_straight(vals):
            unique = sorted(set(vals), reverse=True)
            for i in range(len(unique) - 4):
                window = unique[i:i + 5]
                if window[0] - window[-1] == 4:
                    return True, window[0]
            return False, None

        is_straight, straight_high = get_straight(values)
        is_flush = flush_suit is not None
        is_straight_flush, straight_flush_high = get_straight(flush_cards)

        if is_straight_flush and straight_flush_high == 14:
            return (9, [14], "Royal Flush")

        if is_straight_flush:
            return (8, [straight_flush_high], "Straight Flush")

        if 4 in value_counts.values():
            quad = [v for v, c in value_counts.items() if c == 4][0]
            kicker = max([v for v in values if v != quad])
            return (7, [quad, kicker], "Four of a Kind")

        threes = [v for v, c in value_counts.items() if c == 3]
        pairs = [v for v, c in value_counts.items() if c == 2]

        if threes and (len(threes) > 1 or pairs):
            best_three = max(threes)
            best_pair = max([p for p in pairs if p != best_three] + threes[1:], default=0)
            return (6, [best_three, best_pair], "Full House")

        if is_flush:
            return (5, flush_cards[:5], "Flush")

        if is_straight:
            return (4, [straight_high], "Straight")

        if threes:
            best_three = max(threes)
            kickers = sorted([v for v in values if v != best_three], reverse=True)[:2]
            return (3, [best_three] + kickers, "Three of a Kind")

        if len(pairs) >= 2:
            top_two = sorted(pairs, reverse=True)[:2]
            kicker = max([v for v in values if v not in top_two])
            return (2, top_two + [kicker], "Two Pair")

        if len(pairs) == 1:
            pair = pairs[0]
            kickers = sorted([v for v in values if v != pair], reverse=True)[:3]
            return (1, [pair] + kickers, "One Pair")

        return (0, sorted(values, reverse=True)[:5], "High Card")




@add_show_method
class Roulette(tk.Frame):
    RED_NUMBERS = {1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36}
    BLACK_NUMBERS = {2,4,6,8,10,11,13,15,17,20,22,24,26,28,29,31,33,35}
    
    def __init__(self, parent, main_view):
        super().__init__(parent)
        self.main_view = main_view
        self.bankroll = self.main_view.bankroll
        self.configure(bg="darkgreen")

        self.bet_amount_var = tk.StringVar(value="10")

        self.red_bet_active = tk.BooleanVar()
        self.black_bet_active = tk.BooleanVar()
        self.even_bet_active = tk.BooleanVar()
        self.odd_bet_active = tk.BooleanVar()

        self.red_bet_amount = tk.StringVar(value="10")
        self.black_bet_amount = tk.StringVar(value="10")
        self.even_bet_amount = tk.StringVar(value="10")
        self.odd_bet_amount = tk.StringVar(value="10")

        self.build_ui()

    def show(self):
        self.lift()

    def build_ui(self):
        tk.Label(self, text="Roulette", bg="darkgreen", fg="white", font=("Helvetica", 18)).pack(pady=10)

        # Bankroll display
        self.bankroll_label = tk.Label(self, text=f"Bankroll: ${self.bankroll}", bg="darkgreen", fg="white", font=("Helvetica", 14))
        self.bankroll_label.pack()

        self.selected_numbers = set()  # store selected numbers

        number_grid_frame = tk.Frame(self, bg="darkgreen")
        number_grid_frame.pack(pady=5)

        self.selected_numbers_label = tk.Label(self, text="Selected Numbers: None", bg="darkgreen", fg="white", font=("Helvetica", 12))
        self.selected_numbers_label.pack(pady=(5, 10))

        self.number_buttons = {}

        for i in range(37):
            colorButton = self.get_button_color(i)
            text_color = self.get_text_color(i)
            btn = tk.Button(
                number_grid_frame,
                text=str(i),
                width=4,
                height=2,
                command=lambda n=i: self.toggle_number_selection(n),
                bg=colorButton,
                fg=text_color,
                relief="raised",
                activebackground=colorButton,
                activeforeground=text_color,
                bd=0,
                highlightthickness=0
            )
            row = i // 6
            col = i % 6
            btn.grid(row=row, column=col, padx=2, pady=2)
            btn.config(bg=colorButton, fg=text_color, activebackground=colorButton, activeforeground=text_color)
            self.number_buttons[i] = btn

        self.number_bet_active = tk.BooleanVar(value=True)
        tk.Checkbutton(self, text="Bet on Number(s)", variable=self.number_bet_active,
                    bg="darkgreen", fg="white").pack(pady=5)

        bet_amount_frame = tk.Frame(self, bg="darkgreen")
        bet_amount_frame.pack(pady=10)
        tk.Label(bet_amount_frame, text="Bet Amount per Number:", bg="darkgreen", fg="white").pack(side="left")
        self.bet_amount_entry = tk.Entry(bet_amount_frame, textvariable=self.bet_amount_var, width=10)
        self.bet_amount_entry.pack(side="left", padx=5)

        self.spin_button = tk.Button(self, text="Spin", command=self.spin)
        self.spin_button.pack(pady=10)

        self.result_label = tk.Label(self, text="", bg="darkgreen", fg="yellow", font=("Helvetica", 16))
        self.result_label.pack(pady=10)

        extra_bets_frame = tk.Frame(self, bg="darkgreen")
        extra_bets_frame.pack(pady=10)


        def add_bet_option(label, var, amount_var):
            frame = tk.Frame(extra_bets_frame, bg="darkgreen")
            frame.pack(pady=2, anchor="w")
            tk.Checkbutton(frame, text=label, variable=var, bg="darkgreen", fg="white").pack(side="left")
            tk.Label(frame, text="Amount:", bg="darkgreen", fg="white").pack(side="left")
            tk.Entry(frame, textvariable=amount_var, width=6).pack(side="left")

        add_bet_option("Red", self.red_bet_active, self.red_bet_amount)
        add_bet_option("Black", self.black_bet_active, self.black_bet_amount)
        add_bet_option("Even", self.even_bet_active, self.even_bet_amount)
        add_bet_option("Odd", self.odd_bet_active, self.odd_bet_amount)
    
    def toggle_number_selection(self, number):
        if number in self.selected_numbers:
            self.selected_numbers.remove(number)
            original_bg = self.get_button_color(number)
            original_fg = self.get_text_color(number)
            self.number_buttons[number].config(bg=original_bg, fg=original_fg, relief="raised")
        else:
            self.selected_numbers.add(number)
            self.number_buttons[number].config(bg="yellow", fg="black", relief="sunken")

        self.update_selected_numbers_label()

    def update_selected_numbers_label(self):
        if self.selected_numbers:
            nums = sorted(self.selected_numbers)
            self.selected_numbers_label.config(text=f"Selected Numbers: {', '.join(str(n) for n in nums)}")
        else:
            self.selected_numbers_label.config(text="Selected Numbers: None")

    def get_button_color(self, number):
        if number == 0:
            return "green"
        elif number in self.RED_NUMBERS:
            return "red"
        else:
            return "black"

    def get_text_color(self, number):
        if number == 0 or number in self.RED_NUMBERS:
            return "white"
        else:
            return "lightgray"

    def spin(self):
        bets = []
        total_bet = 0

        if self.number_bet_active.get():
            if not self.selected_numbers:
                messagebox.showerror("No Numbers Selected", "Select at least one number to bet on.")
                return
            try:
                amount = int(self.bet_amount_var.get())
                if amount <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Invalid Bet", "Enter a valid amount for number bet.")
                return

            bets.append({'type': 'number', 'numbers': list(self.selected_numbers), 'amount': amount})
            total_bet += amount * len(self.selected_numbers)

        def add_side_bet(label, var, amount_var, bet_type):
            nonlocal total_bet
            if var.get():
                try:
                    amount = int(amount_var.get())
                    if amount <= 0:
                        raise ValueError
                    bets.append({'type': bet_type, 'amount': amount})
                    total_bet += amount
                except ValueError:
                    messagebox.showerror("Invalid Bet", f"Enter a valid amount for {label} bet.")

        add_side_bet("Red", self.red_bet_active, self.red_bet_amount, "red")
        add_side_bet("Black", self.black_bet_active, self.black_bet_amount, "black")
        add_side_bet("Even", self.even_bet_active, self.even_bet_amount, "even")
        add_side_bet("Odd", self.odd_bet_active, self.odd_bet_amount, "odd")

        if total_bet == 0:
            messagebox.showerror("No Bets", "Please place at least one bet.")
            return

        if total_bet > self.main_view.bankroll:
            messagebox.showerror("Insufficient Funds", f"You need ${total_bet}, but only have ${self.main_view.bankroll}.")
            return

        self.main_view.bankroll -= total_bet
        self.bankroll = self.main_view.bankroll
        self.bankroll_label.config(text=f"Bankroll: ${self.bankroll}")

        result = random.randint(0, 36)
        result_color = "green" if result == 0 else ("red" if result in self.RED_NUMBERS else "black")

        winnings = 0
        messages = []

        for bet in bets:
            btype = bet['type']
            amount = bet['amount']

            if btype == 'number':
                for num in bet['numbers']:
                    if result == num:
                        payout = amount * 35
                        winnings += payout
                        messages.append(f"Hit number {num}! +${payout}")
            elif btype == 'red' and result_color == 'red':
                payout = amount * 2
                winnings += payout
                messages.append(f"Red hit! +${payout}")
            elif btype == 'black' and result_color == 'black':
                payout = amount * 2
                winnings += payout
                messages.append(f"Black hit! +${payout}")
            elif btype == 'even' and result != 0 and result % 2 == 0:
                payout = amount * 2
                winnings += payout
                messages.append(f"Even number hit! +${payout}")
            elif btype == 'odd' and result % 2 == 1:
                payout = amount * 2
                winnings += payout
                messages.append(f"Odd number hit! +${payout}")

        self.main_view.bankroll += winnings
        self.bankroll = self.main_view.bankroll
        self.bankroll_label.config(text=f"Bankroll: ${self.bankroll}")

        if messages:
            self.result_label.config(text=f"Spin result: {result} ({result_color})\n" + "\n".join(messages))
        else:
            self.result_label.config(text=f"Spin result: {result} ({result_color})\nNo wins this time.")

        # After winnings/bankroll updates at the end of spin()
        self.selected_numbers.clear()
        for btn in self.number_buttons.values():
            btn.config(relief="raised")
            num = int(btn["text"])
            if num == 0:
                btn.config(bg="green")
            elif num in self.RED_NUMBERS:
                btn.config(bg="red")
            else:
                btn.config(bg="black")



if __name__ == "__main__":
    root = tk.Tk()
    main = MainView(root)
    main.pack(side="top", fill="both", expand=True)
    root.wm_geometry("900x1300")
    root.mainloop()

                    
