import re
from collections import OrderedDict
from pprint import pprint
from func import tolittle_endian
from json import dumps

"""
r"(\w{8})(\w{2,8})(?=4730|4830|4930)"

(\w{2,8}) > 2 match end with \w{length - 4,length}ae use re.search
"""

def decodetx(txhex):
	if txhex[8:12] == "0001":
		raise RuntimeError("Don't support witness transaction for now.")

	version = txhex[:8]
	locktime = txhex[-8:]
	txhex = txhex[8:-8]

	vin_count = txhex[:2]
	txhex = txhex[2:]

	inputs = []
	for _ in range(int(vin_count)):
		__input = OrderedDict()
		__input["prev_txid"] = txhex[:64]
		__input["prev_vout"] = txhex[64:72]
		txhex = txhex[72:]

		__input["script_length"] = tolittle_endian(re.findall(r"(\w{2,8})(?=4730|4830|4930)", txhex)[0])
		
		sll = len(__input["script_length"]) # script_length length

		# script length
		sl = int(__input["script_length"], 16) * 2
		sl = sl if sl <= 3500 else int(__input["script_length"][-2:], 16) * 2 
		# Something it using an odd number, for example `fdfd00004730..` and the real size of script is `fd` or less than `fd` one or two bytes
		# 3428 should be the maximum of script_length, (16/16)
		# 16 signature(each length <=49), monscript(1byte to m, 1byte to n, 16*(66+2)bytes to public key)

		if sl > 220:
			# multisig
			regex = r"(?=4730|4830|4930)\w{%s,%s}ae"%(sl-6,sl)
			__input["script"] = re.findall(regex, txhex)[0]
			
			l = sll + len( __input["script"])

		else:
			# non-multisig
			l = sll + sl
			__input["script"] = txhex[sl:l]

		__input["sequence"] = txhex[l:l+8]
		inputs.append(__input)
		txhex = txhex[l+8:]

	pprint(inputs)
	

	vout_count = txhex[:2]
	txhex = txhex[2:]
	outputs = []
	for _ in range(int(vout_count, 16)):
		__output = OrderedDict()
		__output["amount"] = txhex[:16]
		__output["script_length"] = txhex[16:18]
		l = 18 + int(__output["script_length"], 16) * 2
		__output["scriptpubkey"] = txhex[18:l]
		outputs.append(__output)
		txhex = txhex[l:]

	tx_json = OrderedDict(
		version = version,
		vin_count = vin_count,
		vin = inputs,
		vout_count = vout_count,
		vout = outputs,
		locktime = locktime

	)

	return dumps(tx_json,  indent = 4)



txhex = "010000000977802a5b8d19874c71b6a78fed12a9ab09c9499e25b149d23c9928c81c03e01700000000fc0047304402201345a1e4d42f665bb36371916f261b6a191b5ab1b73f8978abfcbd9fc9f7bc2502202956f5db9f486f720d7c29d9e6d8ef4bc4d9653fe17cc42dce9fa1b46f912336014730440220725702bb55866da4693de6268fa3558e0faa0dc92de07146b9bf2d719f7838ee02205908211e4e803f586028d06c8b4617ff533b5c8c1aaa821a0062d8aef3e3a9b8014c695221038bbb29a8c3872a4941f16765e194bd906fda0bb56cc3835ceacd8287ce543bc32103fa2f0251b687850cc544a875e92412daca35c3043f08b6cb646526e6a022b7aa2102f79358cc0456c6f4f589458b99338fa7e25a74f88ee9eb8b719cc978c0fd9cf653aeffffffff05fffdfa1fec56baa301e0bf798417617a4999e5f18fdcd17aa4eeb79e2e80a338010000fdfd00004730440220691c4cd78e724e1479515136b71b74afb7f5ce7eebbeb87c7d9c28235f1714ab02202f8ac8e1f848b34df2338daafab96685ee7339a32bd0ca006f7897b71d82ccf8014830450221009b441c7382f5fb739437bfb1723d0ae8db2f1ab31766eec666ffb126d678e8d402200f040bf2b9424e002b34dd594899756a86dc66a08fa767b63bcd22d085efcdba014c695221037586ee03942d1e8e0d81c0cf54bf5e183fcce51fb76ff369ce82bb9e385c1e77210265579ffc66fdeba6d7c5b85341c50c49bdafa5525228244c6dd425bbba2d3cfb21025c5e29bfe0fd4934404ec772571d0134680068a2319d1870b35b32f1c88287de53aeffffffff05fffdfa1fec56baa301e0bf798417617a4999e5f18fdcd17aa4eeb79e2e80a33e010000fdfd0000483045022100ea1bf347b0f14149298003ff23ed8e83474d5c07e81ba318ef2fd7ea4b14e0d202203759a95729d06c2c43829b269f7b0a2de3d4c2ef43cb2d25eb2f04e09f89df890147304402201b182c19069c7fa9d22a1d9f6280b673029e4523873ee057f2ed51c9b2b42f0e02200a67b527b7d6a11c0068b8127f5436e11f9a53eeb8e8871218cdf6c61dfcedd0014c69522103ae51171a6775c357f4bfcf619ab3ac331d333b5907e8944990fdf7183e23c912210220ae8d351437eacc5dfe64704ff8f176cd269c44f19cf8fdfb093340d6890cb32102c302fd432c6bda19df54bc2796254984d2b0a4deb3353b7ef18fc3dd55fa428453aeffffffff57ea9b3258d2f6087d0b0dd046c4bf7899b0a60ac711d5483e8be1dd323365fc08000000fdfe0000483045022100d0aa7940c44d2b833cf0e737bdc9ef6831bd7caaff9c1d73c09a3223f4618ea10220326914809a247d360eda2057f11a3ad792d77dc9d15fd13cd669c2c60919704b01483045022100e652b36e83cd68fcf8eb223e96dc07f6fb5c43b5df9a8222fda920d9f6ff5adb02200c42ad8e38a34be1c65ed9eb0770f0e62c4ce52d6cbd6df6589ec96ee7c42152014c69522103bec977480ae3f5b4617e0f5111d136e44f781da3799aafff89955c9b3670bc5f21036a1c011417f28460e3a8c86fa0b99075be6c4c497cd05545962f320219e5a00721025303cd8aefd09155f8a71fa64f07aac9c49ce23db1de720e343b661398edca3353aeffffffff05fffdfa1fec56baa301e0bf798417617a4999e5f18fdcd17aa4eeb79e2e80a344010000fdfe0000483045022100fd5c4b149bcf72fc387c96081b6e9bea2ca0ed7e6c05a960d372f03fb7721ffd02203fa63055ef7625af2c9c293f38c1250c71ed8443db8d4c9a81153ec88688f15b01483045022100d9781d4959abb494364e5aea042f6fc9e2530518b6e9f5dfedf25cf0743067b5022067deb227e054bebe9c72561777c015423139a7cd8dd5b6d411cedaa0cdc046b8014c695221020a5b39747c3c788ead7b1b7608a463fc2d690716c2e09a73de81136d023590a92103c596a67d823b32ef18cc538d3051189e90f66010293b1c271051a8e7c234a9932102ce4c2c054318f74252bbda2a4cf3234fe1b9035f534619b4fefc95cb250ec45753aeffffffff05fffdfa1fec56baa301e0bf798417617a4999e5f18fdcd17aa4eeb79e2e80a348010000fdfd0000483045022100be475d4c54d1ddce10e09975229c0dbcddfa373fae69c4073909852399bf55a0022029c9b14bcbcb2d31109821570b7ba09faa2dab2605bbb1aeca1e602ccb3413f80147304402204ca7c2b7102915798cef308613f2feac903a7b0ef3d5edf18e0b33198a7bffe5022033f1ac8040f185972c0ee75e639f48cff471d3ef7b9a367cc4bbb3224517f256014c695221037fb1ef6f796d93d9b6304a536d8595a902461744da05f00a777ac048fe4c22f42102b62afd5111eadda781d9ae021d87b91b831804e9dfe93acca914276ed8c1cd24210324769adf308c252f6bd5baa8be7f29575616e568579f808d21b592cd8246d0f653aeffffffff05fffdfa1fec56baa301e0bf798417617a4999e5f18fdcd17aa4eeb79e2e80a34b010000fdfd0000483045022100e809459d943306cfad499879ab1883a341b45c8556153f3f94c4d680918b797102200dde96f60431898ee39134a53d36d3fac51f67d5643faa9257fd70540e61ac580147304402207dbba42a61e388bbb41fa8c3d16447280402a505e3625cc395977d833a966cf00220541d97679b0e69129304f4e67f4b87258e2aba2a15359ca82b10fbcd5a865b01014c695221037f65b82b06d93dfa914cbe78e4a415fc55a56fcb1725157afd39a1c6f8e5f70d2103439818bf52b35dba755a9c0a222da06fb9a18d37b0d2623372022c98707b00352103f6eac6524721219ee1bf55167d3c6e15e30e6a171357d5ddc52749ca092e898b53aeffffffffe8b50866042d7ac79021d06c40f501cc2dfa955519892e276c531c8ab07e750c05000000fc0047304402203d029c99b333fb359c5c488286a241a9827c09d37b0219ee8a21eb358b6180f502207a1ec5cda2f4015e6c9b6736007e822c3325aae480a6f241e1d9a061ec1dfe9c0147304402203212a5cce2e3cc7e550042c217c415451cfe98b49dcd7c9e4beae1eadc71494e02200f5a8b082b5ab3258a7d19027caa90e53666600f82adedb9ac9c662dde95a7aa014c695221037a9b3622852ce6b8ba1c4a14de3946b7a9dd78b081d7380e4fcc8964d7be59172103bf41a2067011da520915f10bfe5dc736adf479e5f844c520ea60acc113e4875121023e3d7cbcfe499394ebd9adbb4b1c3c81ea9368130064903fb42002e84ca6520053aeffffffff406552375829ebecace1df578629f4973e563e284e378a671ce3c20a52454af103000000fdfd000048304502210098a4e1e71f70883fcaaeea3919e3d90a8ea4459a5b7a45f4d5e53ca727f48d700220058cbc75675b0a8821464b88479d6ae82f9596626976f8efc823ba242e150f8301473044022078c532f52f04fd28a2fe2b46d7fbe7bb445314cd071e33ae3a4af243acf2ea050220277c5742732d4a966b2411530a5a05bfda5ae4cf2bdd52ab399319d4e593da45014c69522102d562577c3f23ff0378063c0c41976d69e32fc79960d5d0ee4b34e298f69e6d172103510e3ef43c53dbf28d849b1147698a9f7fc75fda650badfcf57a89c286a324c92102f1501e64d2e85b370d861a8375d0b2a28de5025f295387e73c8df0673fdcbfc453aeffffffff04e071d401000000001976a914ccb74da895be8233281f898636dedda3ffcc154788ac00ca9a3b0000000017a91469f3749b4fa2fee892bb46b779196e1a4fc59a7d87802343000000000017a91469f373d1a34e5b1142289d7efa281cd5d318a51287a70b8e600000000017a914f036fa381fda40f4506d4cfbf27c9279b968e81a8700000000"
txhex = "010000000757cf6cfca66399f560fc68fab76c53c020db7b1320e8653343d8825f22add2d512000000fdfe0000483045022100a8257ccb8a339548455f31b8669ab9de9c4f6158283a691fa16b44ca3ad1d39d02202242c595cb7c3d5741552f8d47b84809fdd111e2b0065eb644e2c9fbd997c78701483045022100d390831c7c83812e00fb933f521e2320e43084bfe097402c9ee9117f5c1cf1a9022065541905ec8bbfde72b7befc42da4525a3a0048ee79dbc1cf6c3c61ca45e9e1e014c69522103d9c83b5c2199d59ea918ec6f939e161c6a6d79faa7397737d9ff962e09c8acb421025a6e6d9a7491a1d501d9769ddd433f1079fc002e266dac25b6ab554e09c9f6632103ad8aca23b25ec06752a0e06fb6f2efc97c149b9786c0adcda4ce878f58a4784f53aeffffffff77155acb2fc854510a83cfc0bc3ce2ba8eab71ed1310ab1370d0d08f25e3f5fb62000000fc0047304402203503fe9e0b5e53b4dc484175c23a2cda5aea43d1259f81586d2fc899e31a1c350220164746ed159ab4ab44b0a2123f011bbef8840a227aedfae70f624858205752fd014730440220368872eaea879775ce3c5f3b2fe270210d65fbbcb87307717891720e67c8db400220778ce199dc48fa038c3107ca6a1693288330bcf5c784904ba98cf9065b36bab3014c695221038b82e7175c1c399a0350cdb4d322640d99c430481f7f77bb13aded1bebcd04902102b97daf83ee10a556c3aff828281e4e1d33c9228c4baab91d47e9f5e5be9fb1bb21027db93168ec672c922e685cc3f19b4d21ee1fac5d0fac6286d9a03b64d3bfe7e953aeffffffff57cf6cfca66399f560fc68fab76c53c020db7b1320e8653343d8825f22add2d508000000fc0047304402205c619994c5bcdea6aa2c719f4a51b7b129ed62f0fd944fdea4bdf20d679e55e0022035193de32bbd46ce238ff3c153c277f6702e200c12d9d8b4ed8a59a54d695d230147304402201a62863861b26b64a81b5d3fcafc52903cc71fbe53dfc4c462d4ecce440da8eb02201893197554bb3a73d1cf0e224cd23293d37444c87e978890c045da4bbfb182eb014c69522102d20a36f9df8f6f685dc62837779206493678a10fc948f4559c7879544d0ee2812102854b032c41db0d9f4cca5f5e4ac26eb50781a79b8e30a8a466fbf660975147f621034d8df3a5d1c666d828fea21324655d6063603bc3f78ba7cce98256fa304ed7da53aeffffffff43dccc51f2d9e9034d8df08cf5d933fc369ec48a789c0aa11a65c95690101b5203000000fdfd00004830450221008902eb2de0d8fdd2d258cb8e36fab762fc6120111149927b5b6c1dad7375004102203dd2fd0a0be45e42c139122548737afedc00fd5eeb6c77aa9987aefa9555732d014730440220347e554b469506ff14065514d11026843725cec6aa42c4ac2b1a2bf40b1c61ee02204ea7d9636e1cb5157974b57812805b1733383479ce06bdeb32acedfc56399b3b014c69522102b1dca4fd8ac8188e402137e97590c39e1714fed161885c982bba87a4322257d921033ae951be7283d483bc80eab51b38d0ad59da81a5f388b3b67f34da843a8043dd2102a1f891cefe5f0bfd6426eaae19afe710b01b281626f20a607e3d610d69caee9b53aeffffffff9b0dfaa881be4e077851967f99af25993c69cfc815b8b61cd8dbf47bd2f2e9924a000000fc00473044022054a4152a9ca55c8acc62bafaf3801660b9e4368f7a711391f38c1c2897e7c41b0220632116a2c8f4ca8171fc7d935b3489725e21a02ea1bf00e500f549c4e3f0cbdd014730440220419fa0d2e9429c129900803f3ad85493b84d0fc4d7052effd412524a3b43b5c20220416ed77c188da9b7cd83a1c0ab7ba6d455ef57b327965dd09f03ee3f11b8d0df014c695221037c3fd47e8ed5c43621cad96de4653b9ba4b3f68bef2ad787e1ed7d24912c736821031694d1e2f3999040c0d72804bba6e51736d569b6752849279ae98ed177c2adfe2103c4b78fd8f0d925c665c3521a2d681fe0779bc3cf2bef8367069fa7272f8074de53aeffffffff7e4b9c7e12d48cbb63e02e40b548d9a5b8bd2fd0b29703a0e039f5e1989f8d1c09000000fdfd000047304402206de2c6480f318086f14c301053ba52b857037b926fd9bc2df1d299f3e170eed1022052980df4a3b122b9b6e45524cea8d5c3c029de782dc8810b5a4560a40ee85e4601483045022100f8a7e1fac84ee523b95af58704dda9436044a94065a8dbab51525a535d14b9150220200c9659d789ef3e5b124cc96aec79070ac7bc3c2ff33d4a92e1ba5888e6a776014c69522102fb489abcd2fc2fdfb59c369316ad5abde8a61c07f00bb8c55f51f782d65de4442102e7cb0774ec96c7640570c8c25bef9347e45481c775f82091d3d19cd8325081a2210247f182921b98915451fc018bb5921e7dc2a20865682a22aa7d69b536c2ef7e0c53aeffffffffff7504e0ab75b0072623634c96e753914dd0b727dbf062ef2cce31587846e46005000000fdfd000047304402202f43d1eb1fab9668f916f917a1af4dbe3025a9fe59338ee5a3eb144d98a9c1fa02202e25b8bea5fbd54a9ae60423a4d7079a4e462e964023e3d23adc566c12b698cd01483045022100c25c6400010705288ab64ea2799a6696e1767e2cd293ddb7d5c3fc31fff719ab02206310247f1199e40143e06cafc1ac19f7c22ae5d18450eb363feeea2bb9bb63d9014c695221024274284b69e2215ac20788e7bfcdc6d68c6518aa00a1db50679bd88ea24a4ba221030261bfc6469b4ec27ff7639e6ed55363b304261581d3eec1aed2a621a9ca82f92102d652b956f5717b05cd58da982c32c66d19050bc649988b4d1a2331ff9e6f815453aeffffffff0f001bb700000000001976a91483468bc54f91bdbb9fcec893c26eefdf548e9bae88ac00879303000000001976a9145d82e828943e35fba43b5c3b86dbeb958a8dda2c88ac80841e00000000001976a914575fda9bfacc18e8237ffb1873b19135b155a7cf88ac804c5614000000001976a914a1a05544ce35835478f2c0e4597c34275fe43b3b88ac00c2eb0b000000001976a914c78289ce70240ef8553b72e6a04621a1ce1756b288ac401640000000000017a914a6d42b31cb160a5c55403026080bf6e79c63b25a87c0fb39000000000017a9142000cc3a6ea27db0c42a741d9d3062435558b1b3878040be030000000017a9147a928f3d8d1c315bdff61ebc6ad360f812e4a9218780de8002000000001976a914bc25b8eab888f9db61ee86e23c9131a2f4bcb97088ac401f7d00000000001976a91450b067a49a985a9ff81087f012d4730922e0d70288ace03cc801000000001976a9147d40eac3fca854827601fd8fb1d936facf229f8288ac80122b01000000001976a91499e3b773189ef2ed1cc754aa1a5b64bac006c7d888ac80c3c901000000001976a914a9f549d837151a44b69057866962a71a351f0f1488ac40e29501000000001976a914a9aaead6819eccbdb887df2da182630cede515f988acfadb80f45400000017a914c51171d6e074fda5dde26b17389b3f3dbf202d928700000000"
print(decodetx(txhex))