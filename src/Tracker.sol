pragma solidity ^0.8.0;

contract Tracker{
    struct Item{
        uint256 id;
        string name;
        address owner;
        string data;
    }

    uint ctr = 1;
    mapping(uint256 => Item) public  id_map;

    event ItemRegistered(uint256 indexed id, address indexed owner, string name);
    event OwnershipTransferred(uint256 indexed id, address indexed from, address indexed to);
    event ItemBurnt(uint256 indexed id);

    function registerItem(string memory name, string memory data) public {
        Item memory new_item = Item(ctr, name, msg.sender, data);
        id_map[ctr] = new_item;
        emit ItemRegistered(ctr++, msg.sender, name);
    }

    function transferOwnership(uint256 id, address newOwner) public {
        require(id_map[id].owner != address(0), "Tracker: Item does not exist.");
        require(msg.sender == id_map[id].owner, "Tracker: Sender is not the owner of item.");
        id_map[id].owner = newOwner;

        emit OwnershipTransferred(id, msg.sender, newOwner);
    }

    function burnItem(uint256 id) public {
        require(id_map[id].owner != address(0), "Tracker: Item does not exist.");
        require(msg.sender == id_map[id].owner, "Tracker: Sender is not the owner of item.");
        delete id_map[id];

        emit ItemBurnt(id);
    }
}