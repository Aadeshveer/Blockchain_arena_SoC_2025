contractAddress = "0x3E364004145956Dac1760c5A15FE78fb8E3f6872"; 

contractABI = [
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "id",
				"type": "uint256"
			}
		],
		"name": "burnItem",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": true,
				"internalType": "uint256",
				"name": "id",
				"type": "uint256"
			}
		],
		"name": "ItemBurnt",
		"type": "event"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": true,
				"internalType": "uint256",
				"name": "id",
				"type": "uint256"
			},
			{
				"indexed": true,
				"internalType": "address",
				"name": "owner",
				"type": "address"
			},
			{
				"indexed": false,
				"internalType": "string",
				"name": "name",
				"type": "string"
			}
		],
		"name": "ItemRegistered",
		"type": "event"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": true,
				"internalType": "uint256",
				"name": "id",
				"type": "uint256"
			},
			{
				"indexed": true,
				"internalType": "address",
				"name": "from",
				"type": "address"
			},
			{
				"indexed": true,
				"internalType": "address",
				"name": "to",
				"type": "address"
			}
		],
		"name": "OwnershipTransferred",
		"type": "event"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "name",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "data",
				"type": "string"
			}
		],
		"name": "registerItem",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "id",
				"type": "uint256"
			},
			{
				"internalType": "address",
				"name": "newOwner",
				"type": "address"
			}
		],
		"name": "transferOwnership",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"name": "id_map",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "id",
				"type": "uint256"
			},
			{
				"internalType": "string",
				"name": "name",
				"type": "string"
			},
			{
				"internalType": "address",
				"name": "owner",
				"type": "address"
			},
			{
				"internalType": "string",
				"name": "data",
				"type": "string"
			}
		],
		"stateMutability": "view",
		"type": "function"
	}
];
connect_wallet_btn = document.getElementById('connect_wallet_btn');
wallet_adress_display = document.getElementById('wallet_address');
dapp_interface = document.getElementById('dapp_interface');
register_item_btn = document.getElementById('register_item_btn');
item_name_input = document.getElementById('item_name_input');
item_data_input = document.getElementById('item_data_input');
item_list = document.getElementById('item_list');
loading_items_message = document.getElementById('loading_items_msg');
history_section = document.getElementById('history_section');
history_item_id = document.getElementById('history_item_id');
provenance_history = document.getElementById('provenance_history');
async function connect_wallet() {
    if (typeof window.ethereum === 'undefined') {
        alert("metamask is not installed");
        return;
    }

    try {
        accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
        provider = new ethers.providers.Web3Provider(window.ethereum);
        signer = provider.getSigner();
        adress = await signer.getAddress();
        wallet_adress_display.innerText = `Connected: ${adress.substring(0, 6)}...${adress.substring(adress.length - 4)}`;
        connect_wallet_btn.disabled = true;
        connect_wallet_btn.innerText = 'Wallet Connected';
        dapp_interface.classList.remove('hidden');
        initialize_dApp();
    } catch (error) {
        alert("Error connecting to metamask", error);
    }
}
function initialize_dApp() {
    contract = new ethers.Contract(contractAddress, contractABI, signer);
    load_all_items();
    listen_for_events();
}

async function load_all_items() {
    loading_items_message.style.display = 'block';
    item_list.innerHTML = '';
    try {
        const registerFilter = contract.filters.ItemRegistered();
        const transferFilter = contract.filters.OwnershipTransferred();
        const burnFilter = contract.filters.ItemBurnt();

        const [registerEvents, transferEvents, burnEvents] = await Promise.all([
            contract.queryFilter(registerFilter, 0, 'latest'),
            contract.queryFilter(transferFilter, 0, 'latest'),
            contract.queryFilter(burnFilter, 0, 'latest')
        ]);
        const burntItemIds = new Set(burnEvents.map(event => event.args.id.toString()));
        const currentOwners = new Map();
        for (const event of registerEvents) {
            currentOwners.set(event.args.id.toString(), event.args.owner);
        }

        for (const event of transferEvents) {
            currentOwners.set(event.args.id.toString(), event.args.to);
        }
        let activeItemCount = 0;
        for (const event of registerEvents) {
            const idString = event.args.id.toString();

            if (!burntItemIds.has(idString)) {
                const itemName = event.args.name;
                const currentOwner = currentOwners.get(idString);
                
                add_item_to_list(event.args.id, currentOwner, itemName);
                activeItemCount++;
            }
        }

        if (activeItemCount === 0) {
             loading_items_message.innerText = "No active items registered yet.";
        } else {
             loading_items_message.style.display = 'none';
        }

    } catch (error) {
        console.error("Unable to fetch items: ", error);
        loading_items_message.innerText = "Error loading items.";
    }
}

async function add_item_to_list(id, owner, name) {
    li = document.createElement('li');
    li.id = `item_${id.toString()}`;
    li.innerHTML = `
        <strong>${name}</strong> (ID: ${id.toString()})
        <div class="item-info">Owner: ${owner}</div>
        <div class="item-actions">
            <div class="transfer-form">
                <input type="text" placeholder="New owner address (0x...)" id="transfer-input-${id.toString()}">
                <button class="action-button" onclick="transfer_item('${id.toString()}')">Transfer</button>
            </div>
            <div>
                <button class="action-button" onclick="view_provenance('${id.toString()}')">View History</button>
                <button class="burn-button" onclick="burn_item('${id.toString()}')">Burn Item</button>
            </div>
        </div>
    `;
    item_list.prepend(li);
}

async function register_item() {
    item_name = item_name_input.value;
    item_data = item_data_input.value;
    if (!item_name) {
        alert("Please enter an item name");
        return;
    }

    try {
        tx = await contract.registerItem(item_name, item_data);
        alert(`Registering "${item_name}"`);
        await tx.wait();
        alert(`Successfully registered "${item_name}"`);
        item_name_input.value = '';
        item_data_input.value = '';
    } catch (error) {
        // console.error("item not registered ", error);
        alert("Failed to register item");
    }
}

async function transfer_item(id_string) {
    new_owner_adress = document.getElementById(`transfer-input-${id_string}`).value;
    if (!ethers.utils.isAddress(new_owner_adress)) {
        alert("invalid address");
        return;
    }

    try {
        tx = await contract.transferOwnership(id_string, new_owner_adress);
        alert(`Transferring Item #${id_string}`);
        await tx.wait();
    } catch (error) {
        console.error("error transferring item:", error);
        alert("Failed to transfer item");
    }
}

async function view_provenance(idString) {
    history_section.classList.remove('hidden');
    history_item_id.innerText = idString;
    provenance_history.innerHTML = '<li>Loading history...</li>';
    try {
        registerFilter = contract.filters.ItemRegistered(idString);
        transferFilter = contract.filters.OwnershipTransferred(idString);
        registerEvents = await contract.queryFilter(registerFilter, 0, 'latest');
        transferEvents = await contract.queryFilter(transferFilter, 0, 'latest');
        allHistoryEvents = [...registerEvents, ...transferEvents].sort((a,b) => a.blockNumber - b.blockNumber);
        provenance_history.innerHTML = '';
        if (allHistoryEvents.length === 0) {
            provenance_history.innerHTML = '<li>No history found.</li>';
            return;
        }
        
        allHistoryEvents.forEach(event => {
            li = document.createElement('li');
            if (event.event === "ItemRegistered") {
                li.innerHTML = `<strong>Registered:</strong> Item created and assigned to <div class="item-info">${event.args.owner}</div>`;
            } else if (event.event === "OwnershipTransferred") {
                 li.innerHTML = `<strong>Transferred:</strong> From <div class="item_info">${event.args.from}</div> To <div class="item_info">${event.args.to}</div>`;
            }
            provenance_history.appendChild(li);
        });
    } catch (error) {
        console.error("error fetching provenance: ", error);
        provenance_history.innerHTML = '<li> Error fetching history. </li>';
    }
}

async function burn_item(idString) {
    try {
        const tx = await contract.burnItem(idString);
        alert(`Burning Item #${idString}.`);
        await tx.wait();
        alert(`Item #${idString} has been successfully burned.`);
    } catch (error) {
        alert("Failed to burn item.");
    }
}

connect_wallet_btn.addEventListener('click', connect_wallet);
register_item_btn.addEventListener('click', register_item);