import datetime as _dt
import hashlib as _hashlib
import json as _json
from typing import Dict, List


class Blockchain:
    def __init__(self) -> None:
        self.chain: List[Dict] = []
        genesis_block = self._create_block(
            sender="System",
            receiver="Genesis",
            amount=0,
            price=0,
            proof=1,
            previous_hash="0",
            index=1,
        )
        self.chain.append(genesis_block)

    def get_chain(self):
        return self.chain

    def mine_block(
        self, sender: str, receiver: str, amount: float, price: float
    ) -> dict:
        previous_block = self.get_previous_block()
        previous_proof = previous_block["proof"]
        index = len(self.chain) + 1
        proof = self._proof_of_work(previous_proof, index, sender, receiver, amount, price)
        previous_hash = self._hash(block=previous_block)

        block = self._create_block(sender, receiver, amount, price, proof, previous_hash, index)
        self.chain.append(block)

        return block

    def _hash(self, block: Dict) -> str:
        encoded_block = _json.dumps(block, sort_keys=True).encode()
        return _hashlib.sha256(encoded_block).hexdigest()

    def _to_digest(self, new_proof: int, previous_proof: int, index: int, sender: str, receiver: str, amount: float, price: float) -> bytes:
        to_digest = str(new_proof ** 2 - previous_proof ** 2 + index) + sender + receiver + str(amount) + str(price)
        return to_digest.encode()

    def _proof_of_work(self, previous_proof: int, index: int, sender: str, receiver: str, amount: float, price: float) -> int:
        new_proof = 1
        check_proof = False

        while not check_proof:
            to_digest = self._to_digest(new_proof, previous_proof, index, sender, receiver, amount, price)
            hash_operation = _hashlib.sha256(to_digest).hexdigest()
            if hash_operation[:4] == "0000":
                check_proof = True
            else:
                new_proof += 1

        return new_proof

    def get_previous_block(self) -> Dict:
        return self.chain[-1]

    def _create_block(self, sender: str, receiver: str, amount: float, price: float, proof: int, previous_hash: str, index: int) -> Dict:
        block = {
            "index": index,
            "timestamp": str(_dt.datetime.now()),
            "sender": sender,
            "receiver": receiver,
            "amount": amount,
            "price": price,
            "proof": proof,
            "previous_hash": previous_hash,
        }
        return block

    def is_chain_valid(self) -> bool:
        previous_block = self.chain[0]
        block_index = 1

        while block_index < len(self.chain):
            block = self.chain[block_index]

            if block["previous_hash"] != self._hash(previous_block):
                return False

            previous_proof = previous_block["proof"]
            index, sender, receiver, amount, price, proof = (
                block["index"], block["sender"], block["receiver"], block["amount"], block["price"], block["proof"]
            )

            hash_operation = _hashlib.sha256(
                self._to_digest(proof, previous_proof, index, sender, receiver, amount, price)
            ).hexdigest()

            if hash_operation[:4] != "0000":
                return False

            previous_block = block
            block_index += 1

        return True
